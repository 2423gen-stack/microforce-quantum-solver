import numpy as np
from microforce_solver import MicroforceQuantumSolver

# --- テスト問題設定 (トイケース: M=3個の長方形) ---
M = 3
# 各長方形が必ず含まなければならない指定点 (x, y)
points = [
    (100.0, 100.0),
    (150.0, 120.0),
    (300.0, 400.0)
]
# 各長方形の目標面積
target_areas = [
    10000.0,  # 100x100 相当
    15000.0,  # 122x122 相当
    20000.0   # 141x141 相当
]

# --- 1. 境界 & サイズ整合性射影 (Boundary & Size Projection) ---
def project_boundaries(x):
    x_new = x.copy()
    for i in range(M):
        idx = 4 * i
        # 領域 [0, 10000] にクリップ
        x_new[idx] = max(0.0, min(10000.0, x_new[idx]))
        x_new[idx+1] = max(0.0, min(10000.0, x_new[idx+1]))
        x_new[idx+2] = max(0.0, min(10000.0, x_new[idx+2]))
        x_new[idx+3] = max(0.0, min(10000.0, x_new[idx+3]))
        
        # 幅と高さの最低保証 (1以上)
        if x_new[idx+2] < x_new[idx] + 1.0:
            mid = (x_new[idx] + x_new[idx+2]) / 2.0
            x_new[idx] = max(0.0, mid - 0.5)
            x_new[idx+2] = min(10000.0, mid + 0.5)
        if x_new[idx+3] < x_new[idx+1] + 1.0:
            mid = (x_new[idx+1] + x_new[idx+3]) / 2.0
            x_new[idx+1] = max(0.0, mid - 0.5)
            x_new[idx+3] = min(10000.0, mid + 0.5)
    return x_new

# --- 2. 点内包射影 (Point Containment Projection) ---
def project_points(x):
    x_new = x.copy()
    for i in range(M):
        idx = 4 * i
        px, py = points[i]
        
        # x_i1 <= px <= x_i2
        if x_new[idx] > px:
            x_new[idx] = px
        if x_new[idx+2] < px:
            x_new[idx+2] = px
            
        # y_i1 <= py <= y_i2
        if x_new[idx+1] > py:
            x_new[idx+1] = py
        if x_new[idx+3] < py:
            x_new[idx+3] = py
    return x_new

# --- 3. 重なり防止射影 (Non-overlap Projection) ---
def project_non_overlap(x):
    x_new = x.copy()
    # 全ペア間で重なりがあれば、最小移動距離で押し出す
    for i in range(M):
        for j in range(i + 1, M):
            idx_i = 4 * i
            idx_j = 4 * j
            
            ax1, ay1, ax2, ay2 = x_new[idx_i], x_new[idx_i+1], x_new[idx_i+2], x_new[idx_i+3]
            bx1, by1, bx2, by2 = x_new[idx_j], x_new[idx_j+1], x_new[idx_j+2], x_new[idx_j+3]
            
            # 重なり幅の計算
            overlap_x = min(ax2, bx2) - max(ax1, bx1)
            overlap_y = min(ay2, by2) - max(ay1, by1)
            
            if overlap_x > 0 and overlap_y > 0:
                # 重なり解消のためのX/Y方向の最小押し出し量を選択
                if overlap_x < overlap_y:
                    shift = overlap_x / 2.0
                    if (ax1 + ax2) < (bx1 + bx2):
                        # Aは左へ、Bは右へ
                        x_new[idx_i] -= shift
                        x_new[idx_i+2] -= shift
                        x_new[idx_j] += shift
                        x_new[idx_j+2] += shift
                    else:
                        # Aは右へ、Bは左へ
                        x_new[idx_i] += shift
                        x_new[idx_i+2] += shift
                        x_new[idx_j] -= shift
                        x_new[idx_j+2] -= shift
                else:
                    shift = overlap_y / 2.0
                    if (ay1 + ay2) < (by1 + by2):
                        # Aは上へ、Bは下へ
                        x_new[idx_i+1] -= shift
                        x_new[idx_i+3] -= shift
                        x_new[idx_j+1] += shift
                        x_new[idx_j+3] += shift
                    else:
                        # Aは下へ、Bは上へ
                        x_new[idx_i+1] += shift
                        x_new[idx_i+3] += shift
                        x_new[idx_j+1] -= shift
                        x_new[idx_j+3] -= shift
    return x_new

# --- 4. 面積目標射影 (Target Area Projection) ---
def project_target_areas(x):
    x_new = x.copy()
    for i in range(M):
        idx = 4 * i
        px, py = points[i]
        r = target_areas[i]
        
        ax1, ay1, ax2, ay2 = x_new[idx], x_new[idx+1], x_new[idx+2], x_new[idx+3]
        
        # 指定点から各境界までの距離
        dx1 = max(0.1, px - ax1)
        dx2 = max(0.1, ax2 - px)
        dy1 = max(0.1, py - ay1)
        dy2 = max(0.1, ay2 - py)
        
        current_w = dx1 + dx2
        current_h = dy1 + dy2
        current_area = current_w * current_h
        
        if current_area > 0:
            # 目標面積と現在面積の比からスケーリング係数を算出
            scale = np.sqrt(r / current_area)
            
            # 指定点を軸として拡大・縮小
            x_new[idx] = px - dx1 * scale
            x_new[idx+1] = py - dy1 * scale
            x_new[idx+2] = px + dx2 * scale
            x_new[idx+3] = py + dy2 * scale
    return x_new


# --- 5. ソルバーの実行 ---
def main():
    print("=== Microforce Quantum Solver v2 Verification ===")
    
    # 各長方形の初期配置（指定点を中心とする10x10の微小長方形からスタート）
    x_init = []
    for px, py in points:
        x_init.extend([px - 5.0, py - 5.0, px + 5.0, py + 5.0])
    
    # ソルバーのインスタンス化 (次元数 = 4 * M)
    solver = MicroforceQuantumSolver(n_dim=4*M, x_init=x_init)
    
    # 各制約レイヤーの追加 (重要度ウェイトを調整可能)
    # 物理法則（点内包、境界、重なり防止）の優先度を高めに設定
    solver.add_constraint_layer(project_boundaries, weight=1.0)
    solver.add_constraint_layer(project_points, weight=1.5)
    solver.add_constraint_layer(project_non_overlap, weight=2.0)
    solver.add_constraint_layer(project_target_areas, weight=1.0)
    
    # 交互射影法 (POCS) にて収束させてみる
    print("\n--- 1. 交互射影法 (POCS) による厳密交差の結晶化 ---")
    success, iters, final_diff = solver.solve_pocs(max_iter=200, tol=1e-4)
    x_opt = solver.get_state()
    
    print(f"POCS終了: 成功={success}, イテレーション={iters}, 最終変化量={final_diff:.6f}")
    for i in range(M):
        idx = 4 * i
        x1, y1, x2, y2 = x_opt[idx:idx+4]
        w = x2 - x1
        h = y2 - y1
        area = w * h
        print(f"長方形 {i}: 座標=[{x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f}], 幅={w:.1f}, 高さ={h:.1f}, 面積={area:.1f} (目標={target_areas[i]})")

    # 平均射影法 (Harmonic) による調和解決
    print("\n--- 2. 平均射影法 (Harmonic) による調和解決 ---")
    solver_harmonic = MicroforceQuantumSolver(n_dim=4*M, x_init=x_init)
    solver_harmonic.add_constraint_layer(project_boundaries, weight=1.0)
    solver_harmonic.add_constraint_layer(project_points, weight=2.0)
    solver_harmonic.add_constraint_layer(project_non_overlap, weight=2.0)
    solver_harmonic.add_constraint_layer(project_target_areas, weight=1.0)
    
    success, iters, final_diff = solver_harmonic.solve_harmonic(max_iter=200, tol=1e-4)
    x_opt_h = solver_harmonic.get_state()
    
    print(f"Harmonic終了: 成功={success}, イテレーション={iters}, 最終変化量={final_diff:.6f}")
    for i in range(M):
        idx = 4 * i
        x1, y1, x2, y2 = x_opt_h[idx:idx+4]
        w = x2 - x1
        h = y2 - y1
        area = w * h
        print(f"長方形 {i}: 座標=[{x1:.1f}, {y1:.1f}, {x2:.1f}, {y2:.1f}], 幅={w:.1f}, 高さ={h:.1f}, 面積={area:.1f} (目標={target_areas[i]})")

if __name__ == "__main__":
    main()
