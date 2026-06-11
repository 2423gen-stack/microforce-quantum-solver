import numpy as np

class MicroforceQuantumSolver:
    """
    Microforce Quantum Solver v2 (Core Engine)
    多次元ベクトル空間上における、複数の制約レイヤーの重ね合わせと結晶化を行う数理ソルバー。
    交互射影法 (POCS) および 平均射影法 (Harmonic/Relaxation) を実装。
    """
    def __init__(self, n_dim, x_init=None):
        """
        n_dim: 状態ベクトルの次元数
        x_init: 初期状態ベクトル (Noneの場合はゼロ初期化)
        """
        self.n_dim = n_dim
        if x_init is not None:
            self.x = np.array(x_init, dtype=float)
        else:
            self.x = np.zeros(n_dim, dtype=float)
            
        self.projections = []  # 各制約レイヤーの射影関数リスト
        self.weights = []      # 各制約レイヤーの重み（重要度）

    def add_constraint_layer(self, proj_func, weight=1.0):
        """
        制約レイヤー（射影関数）を追加する。
        proj_func: 現在の状態ベクトル x (np.array) を受け取り、
                   制約を満たすように修正した新しいベクトル x_new (np.array) を返す関数。
        weight: 平均射影時の重み（重要度）
        """
        self.projections.append(proj_func)
        self.weights.append(weight)

    def solve_pocs(self, max_iter=100, tol=1e-5):
        """
        交互射影法 (POCS: Projection onto Convex Sets)
        すべての制約の「積集合（交点）」を、順次射影の反復により厳密に計算する。
        """
        for i in range(max_iter):
            x_old = self.x.copy()
            
            # 各制約レイヤーを順番に適用（重ね合わせ）
            for proj in self.projections:
                self.x = proj(self.x)
                
            # 変化量が許容値以下になったら収束（結晶化）
            diff = np.linalg.norm(self.x - x_old)
            if diff < tol:
                return True, i + 1, diff
                
        return False, max_iter, np.linalg.norm(self.x - x_old)

    def solve_harmonic(self, max_iter=100, tol=1e-5):
        """
        平均射影法 (Harmonic Projection)
        矛盾する制約（オーバーコンストレイント）が存在する場合に、
        各制約からの距離の二乗和が最小となる「調和点（最小二乗点）」を計算する。
        """
        n_layers = len(self.projections)
        if n_layers == 0:
            return True, 0, 0.0

        # 重みの正規化
        w_arr = np.array(self.weights, dtype=float)
        w_arr /= np.sum(w_arr)

        for i in range(max_iter):
            x_old = self.x.copy()
            x_new = np.zeros_like(self.x)
            
            # 各制約レイヤーへの射影の重み付き平均を取る（葛藤の緩和）
            for proj, w in zip(self.projections, w_arr):
                x_new += w * proj(self.x)
                
            self.x = x_new
            
            # 収束判定
            diff = np.linalg.norm(self.x - x_old)
            if diff < tol:
                return True, i + 1, diff
                
        return False, max_iter, np.linalg.norm(self.x - x_old)

    def get_state(self):
        """
        現在の結晶化された状態ベクトルを取得する。
        """
        return self.x.copy()
