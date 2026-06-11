import os
import sys
import json
import numpy as np
from pydantic import BaseModel, Field
from typing import List
from google import genai
from google.genai import types

from microforce_solver import MicroforceQuantumSolver

# --- 1. LLM出力のPydanticスキーマ定義 ---
class Bounds(BaseModel):
    min_x: float = Field(description="空間の最小X座標")
    min_y: float = Field(description="空間の最小Y座標")
    max_x: float = Field(description="空間の最大X座標")
    max_y: float = Field(description="空間の最大Y座標")

class TenantObject(BaseModel):
    id: int = Field(description="ユニークなオブジェクトID")
    name: str = Field(description="オブジェクト（店舗）の名称")
    point: List[float] = Field(description="必須通過点 [x, y]")
    target_area: float = Field(description="目標とする専有面積")

class Constraint(BaseModel):
    type: str = Field(description="制約の種類: 'boundary_limit', 'point_containment', 'non_overlap', 'area_scaling'")
    weight: float = Field(description="制約の重要度（重み）")

class GeometricProblem(BaseModel):
    bounds: Bounds = Field(description="空間全体の境界情報")
    objects: List[TenantObject] = Field(description="配置するオブジェクトの一覧")
    constraints: List[Constraint] = Field(description="適用する制約ルールと重みの一覧")

# --- 2. 幾何射影関数のファクトリ（動的ビルド用） ---
def build_projection_functions(problem: GeometricProblem):
    M = len(problem.objects)
    points = [obj.point for obj in problem.objects]
    target_areas = [obj.target_area for obj in problem.objects]
    b = problem.bounds
    
    # 境界制約
    def project_boundaries(x):
        x_new = x.copy()
        for i in range(M):
            idx = 4 * i
            x_new[idx] = max(b.min_x, min(b.max_x, x_new[idx]))
            x_new[idx+1] = max(b.min_y, min(b.max_y, x_new[idx+1]))
            x_new[idx+2] = max(b.min_x, min(b.max_x, x_new[idx+2]))
            x_new[idx+3] = max(b.min_y, min(b.max_y, x_new[idx+3]))
            
            # 最小幅・高さ (1.0) 保証
            if x_new[idx+2] < x_new[idx] + 1.0:
                mid = (x_new[idx] + x_new[idx+2]) / 2.0
                x_new[idx] = max(b.min_x, mid - 0.5)
                x_new[idx+2] = min(b.max_x, mid + 0.5)
            if x_new[idx+3] < x_new[idx+1] + 1.0:
                mid = (x_new[idx+1] + x_new[idx+3]) / 2.0
                x_new[idx+1] = max(b.min_y, mid - 0.5)
                x_new[idx+3] = min(b.max_y, mid + 0.5)
        return x_new

    # 点内包制約
    def project_points(x):
        x_new = x.copy()
        for i in range(M):
            idx = 4 * i
            px, py = points[i][0], points[i][1]
            if x_new[idx] > px:
                x_new[idx] = px
            if x_new[idx+2] < px:
                x_new[idx+2] = px
            if x_new[idx+1] > py:
                x_new[idx+1] = py
            if x_new[idx+3] < py:
                x_new[idx+3] = py
        return x_new

    # 重なり防止制約
    def project_non_overlap(x):
        x_new = x.copy()
        for i in range(M):
            for j in range(i + 1, M):
                idx_i = 4 * i
                idx_j = 4 * j
                
                ax1, ay1, ax2, ay2 = x_new[idx_i], x_new[idx_i+1], x_new[idx_i+2], x_new[idx_i+3]
                bx1, by1, bx2, by2 = x_new[idx_j], x_new[idx_j+1], x_new[idx_j+2], x_new[idx_j+3]
                
                overlap_x = min(ax2, bx2) - max(ax1, bx1)
                overlap_y = min(ay2, by2) - max(ay1, by1)
                
                if overlap_x > 0 and overlap_y > 0:
                    if overlap_x < overlap_y:
                        shift = overlap_x / 2.0
                        if (ax1 + ax2) < (bx1 + bx2):
                            x_new[idx_i] -= shift
                            x_new[idx_i+2] -= shift
                            x_new[idx_j] += shift
                            x_new[idx_j+2] += shift
                        else:
                            x_new[idx_i] += shift
                            x_new[idx_i+2] += shift
                            x_new[idx_j] -= shift
                            x_new[idx_j+2] -= shift
                    else:
                        shift = overlap_y / 2.0
                        if (ay1 + ay2) < (by1 + by2):
                            x_new[idx_i+1] -= shift
                            x_new[idx_i+3] -= shift
                            x_new[idx_j+1] += shift
                            x_new[idx_j+3] += shift
                        else:
                            x_new[idx_i+1] += shift
                            x_new[idx_i+3] += shift
                            x_new[idx_j+1] -= shift
                            x_new[idx_j+3] -= shift
        return x_new

    # 面積目標制約
    def project_target_areas(x):
        x_new = x.copy()
        for i in range(M):
            idx = 4 * i
            px, py = points[i][0], points[i][1]
            r = target_areas[i]
            
            ax1, ay1, ax2, ay2 = x_new[idx], x_new[idx+1], x_new[idx+2], x_new[idx+3]
            
            dx1 = max(0.1, px - ax1)
            dx2 = max(0.1, ax2 - px)
            dy1 = max(0.1, py - ay1)
            dy2 = max(0.1, ay2 - py)
            
            current_w = dx1 + dx2
            current_h = dy1 + dy2
            current_area = current_w * current_h
            
            if current_area > 0:
                scale = np.sqrt(r / current_area)
                x_new[idx] = px - dx1 * scale
                x_new[idx+1] = py - dy1 * scale
                x_new[idx+2] = px + dx2 * scale
                x_new[idx+3] = py + dy2 * scale
        return x_new

    return {
        "boundary_limit": project_boundaries,
        "point_containment": project_points,
        "non_overlap": project_non_overlap,
        "area_scaling": project_target_areas
    }

# --- 3. メインパイプライン ---
def main():
    if len(sys.argv) < 2:
        print("使用法: python3 requirement_compiler.py <requirement_markdown_file>")
        sys.exit(1)
        
    md_file = sys.argv[1]
    if not os.path.exists(md_file):
        print(f"エラー: ファイルが見つかりません: {md_file}")
        sys.exit(1)
        
    # 3.1 Markdownファイルの読み込み
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
        
    print(f"=== 1. Markdownの読み込み完了 ({md_file}) ===")
    
    # 3.2 Gemini APIによる構造化コンパイル
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("エラー: 環境変数 GEMINI_API_KEY が設定されていません。")
        sys.exit(1)
        
    print("=== 2. LLMによる幾何パラメータへのコンパイル開始... ===")
    client = genai.Client()
    
    prompt = f"""
    あなたは優秀なMicroforce幾何学コンパイラ（LLM Compiler）です。
    以下のMarkdownで記述された要件仕様書を解析し、幾何ソルバーに直結可能な構造化JSONへ翻訳（コンパイル）してください。
    
    [要件仕様書]
    {md_content}
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GeometricProblem
            )
        )
        # 構造化されたPydanticインスタンスへパース
        problem_data = json.loads(response.text)
        problem = GeometricProblem(**problem_data)
        print("コンパイル成功！幾何パラメータJSON:")
        print(json.dumps(problem_data, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"コンパイル失敗: {str(e)}")
        sys.exit(1)
        
    # 3.3 ソルバーの組み立てと実行
    print("\n=== 3. 幾何ソルバーの動的ビルドと実行開始... ===")
    M = len(problem.objects)
    
    # 初期配置（指定点を中心とする10x10の微小長方形からスタート）
    x_init = []
    for obj in problem.objects:
        px, py = obj.point[0], obj.point[1]
        x_init.extend([px - 5.0, py - 5.0, px + 5.0, py + 5.0])
        
    solver = MicroforceQuantumSolver(n_dim=4*M, x_init=x_init)
    
    # 動的射影マッピングの作成
    proj_map = build_projection_functions(problem)
    
    # 制約レイヤーの登録
    for constraint in problem.constraints:
        c_type = constraint.type
        if c_type in proj_map:
            solver.add_constraint_layer(proj_map[c_type], weight=constraint.weight)
            print(f"制約レイヤー追加: {c_type} (重み: {constraint.weight})")
        else:
            print(f"警告: 未定義の制約タイプを無視します: {c_type}")
            
    # 調和解決（Harmonic Projection）の実行
    print("\n=== 4. 数理推論（平均射影/調和解決）の開始... ===")
    success, iters, final_diff = solver.solve_harmonic(max_iter=300, tol=1e-4)
    x_opt = solver.get_state()
    
    print(f"解決完了: 成功={success}, 反復回数={iters}, 最終変化量={final_diff:.6f}")
    
    # 結果のデコードと出力
    output_objects = []
    for i, obj in enumerate(problem.objects):
        idx = 4 * i
        x1, y1, x2, y2 = x_opt[idx:idx+4]
        w = x2 - x1
        h = y2 - y1
        area = w * h
        
        tenant_result = {
            "name": obj.name,
            "target_point": obj.point,
            "allocated_area": {
                "top_left": [float(x1), float(y1)],
                "bottom_right": [float(x2), float(y2)],
                "width": float(w),
                "height": float(h),
                "area": float(area)
            },
            "target_area": obj.target_area,
            "area_achievement_ratio": float(area / obj.target_area)
        }
        output_objects.append(tenant_result)
        
        print(f"[{obj.name}]:")
        print(f"  配置座標: 左上=[{x1:.1f}, {y1:.1f}], 右下=[{x2:.1f}, {y2:.1f}]")
        print(f"  サイズ  : 幅={w:.1f}, 高さ={h:.1f}, 面積={area:.1f} (目標={obj.target_area}) (達成率: {area/obj.target_area:.2%})")

    # 結果JSONの保存
    out_file = "output_solution.json"
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(output_objects, f, indent=2, ensure_ascii=False)
    print(f"\n最終結果を {out_file} に保存しましたわ！")

if __name__ == "__main__":
    main()
