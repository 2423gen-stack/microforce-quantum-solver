import numpy as np
from typing import List, Dict, Any

class GeometryPrimitive:
    """N次元幾何オブジェクトの基底クラス"""
    def project(self, x: np.ndarray) -> np.ndarray:
        """状態ベクトル x をこの幾何オブジェクトに直交射影したベクトルを返す"""
        raise NotImplementedError

class Hyperplane(GeometryPrimitive):
    """超平面: a^T x = b"""
    def __init__(self, a: np.ndarray, b: float):
        self.a = np.array(a, dtype=float)
        self.b = float(b)
        self.norm_sq = np.sum(self.a ** 2)
        if self.norm_sq < 1e-12:
            raise ValueError("法線ベクトル a の長さが 0 に近すぎます。")

    def project(self, x: np.ndarray) -> np.ndarray:
        # P(x) = x - ((a^T x - b) / ||a||^2) * a
        dot_diff = np.dot(self.a, x) - self.b
        return x - (dot_diff / self.norm_sq) * self.a

class HalfSpace(GeometryPrimitive):
    """半空間 (不等式制約): a^T x <= b"""
    def __init__(self, a: np.ndarray, b: float):
        self.a = np.array(a, dtype=float)
        self.b = float(b)
        self.norm_sq = np.sum(self.a ** 2)
        if self.norm_sq < 1e-12:
            raise ValueError("法線ベクトル a の長さが 0 に近すぎます。")

    def project(self, x: np.ndarray) -> np.ndarray:
        dot_diff = np.dot(self.a, x) - self.b
        if dot_diff <= 0:
            return x.copy()
        return x - (dot_diff / self.norm_sq) * self.a

class BoxConstraint(GeometryPrimitive):
    """境界制約 (各軸ごとの独立した上下限): lower <= x <= upper"""
    def __init__(self, lower: np.ndarray, upper: np.ndarray):
        self.lower = np.array(lower, dtype=float)
        self.upper = np.array(upper, dtype=float)
        if np.any(self.lower > self.upper):
            raise ValueError("下限が上限を上回っている軸が存在します。")

    def project(self, x: np.ndarray) -> np.ndarray:
        return np.clip(x, self.lower, self.upper)

class Hypersphere(GeometryPrimitive):
    """超球: ||x - center||_2 <= radius"""
    def __init__(self, center: np.ndarray, radius: float):
        self.center = np.array(center, dtype=float)
        self.radius = float(radius)
        if self.radius < 0:
            raise ValueError("半径は 0 以上である必要があります。")

    def project(self, x: np.ndarray) -> np.ndarray:
        diff = x - self.center
        dist = np.linalg.norm(diff)
        if dist <= self.radius:
            return x.copy()
        if dist < 1e-12:
            return self.center.copy()
        return self.center + (diff / dist) * self.radius

class AffineSubspace(GeometryPrimitive):
    """アフィン部分空間: A x = b (線形方程式系)"""
    def __init__(self, A: np.ndarray, b: np.ndarray):
        self.A = np.array(A, dtype=float)
        self.b = np.array(b, dtype=float)
        # 擬似逆行列の事前計算
        self.pinv_A = np.linalg.pinv(self.A)

    def project(self, x: np.ndarray) -> np.ndarray:
        # P(x) = x - A^+ (A x - b)
        return x - np.dot(self.pinv_A, np.dot(self.A, x) - self.b)

class MultiDimensionalGeometricSolver:
    """N次元空間上の幾何制約ソルバー (POCS / 調和平均射影)"""
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.primitives: List[GeometryPrimitive] = []
        self.weights: List[float] = []

    def add_constraint(self, primitive: GeometryPrimitive, weight: float = 1.0):
        """制約オブジェクトとその葛藤調整ウェイトを登録"""
        self.primitives.append(primitive)
        self.weights.append(float(weight))

    def solve(self, 
              x_init: np.ndarray, 
              method: str = "harmonic", 
              max_iter: int = 1000, 
              tol: float = 1e-7) -> Dict[str, Any]:
        """
        指定された初期値から反復射影により最適解を計算する。
        method: "pocs" (交互射影 / 連続射影) または "harmonic" (重み付き平均射影 / 葛藤最小化)
        """
        x = np.array(x_init, dtype=float).copy()
        if len(x) != self.dimension:
            raise ValueError(f"初期ベクトル次元数 ({len(x)}) がソルバー次元数 ({self.dimension}) と一致しません。")

        if not self.primitives:
            return {"success": True, "x": x, "iterations": 0, "residual": 0.0}

        weights = np.array(self.weights)
        weights /= np.sum(weights)  # 重みの正規化

        success = False
        residual = 0.0
        
        for iteration in range(max_iter):
            x_prev = x.copy()
            
            if method == "pocs":
                # POCS: 順次射影
                for primitive in self.primitives:
                    x = primitive.project(x)
            elif method == "harmonic":
                # Harmonic: 各制約射影の重み付き平均
                x_next = np.zeros_like(x)
                for primitive, w in zip(self.primitives, weights):
                    x_next += w * primitive.project(x)
                x = x_next
            else:
                raise ValueError(f"未知の解決手法: {method}")

            # 収束判定 (前ステップからの変化量)
            residual = np.linalg.norm(x - x_prev)
            if residual < tol:
                success = True
                break
        
        # 最終状態での各制約との残差（射影距離）を評価
        constraint_errors = []
        for primitive in self.primitives:
            proj = primitive.project(x)
            error = np.linalg.norm(x - proj)
            constraint_errors.append(error)

        return {
            "success": success,
            "x": x,
            "iterations": iteration + 1,
            "residual": residual,
            "constraint_errors": constraint_errors
        }
