import numpy as np
from microforce_geometry import (
    Hyperplane,
    HalfSpace,
    BoxConstraint,
    Hypersphere,
    AffineSubspace,
    MultiDimensionalGeometricSolver
)

def test_3d_pocs_planes():
    print("=== テスト1: 3次元空間における複数平面の交点 (POCS) ===")
    # 3つの平面が交わる点は一意に [1.0, 1.0, 1.0]
    # 平面1: x1 + x2 + x3 = 3
    # 平面2: x1 - x2 = 0
    # 平面3: x2 - x3 = 0
    p1 = Hyperplane(a=np.array([1.0, 1.0, 1.0]), b=3.0)
    p2 = Hyperplane(a=np.array([1.0, -1.0, 0.0]), b=0.0)
    p3 = Hyperplane(a=np.array([0.0, 1.0, -1.0]), b=0.0)

    solver = MultiDimensionalGeometricSolver(dimension=3)
    solver.add_constraint(p1)
    solver.add_constraint(p2)
    solver.add_constraint(p3)

    # 離れた初期値からスタート
    x_init = np.array([10.0, -5.0, 3.0])
    result = solver.solve(x_init, method="pocs", tol=1e-9)

    print(f"結果成功: {result['success']}")
    print(f"反復回数: {result['iterations']}")
    print(f"収束座標: {result['x']}")
    print(f"残差: {result['residual']}")
    
    # 期待値 [1, 1, 1] との誤差検証
    assert np.allclose(result['x'], np.array([1.0, 1.0, 1.0]), atol=1e-6)
    print("テスト1 成功!\n")

def test_2d_harmonic_spheres():
    print("=== テスト2: 2次元空間における交わらない超球の調和解決 ===")
    # 3つの互いに交わらない円（超球）
    # 円1: 中心 [0, 0], 半径 0.5 (この内側に点を入れたい)
    # 円2: 中心 [4, 0], 半径 0.5
    # 円3: 中心 [2, 3], 半径 0.5
    # 交わりがないため、POCSでは振動するが、調和平均(Harmonic)では3つの中心の重心付近に釣り合う
    s1 = Hypersphere(center=np.array([0.0, 0.0]), radius=0.0)
    s2 = Hypersphere(center=np.array([4.0, 0.0]), radius=0.0)
    s3 = Hypersphere(center=np.array([2.0, 3.0]), radius=0.0)

    solver = MultiDimensionalGeometricSolver(dimension=2)
    # 均等な重みで追加
    solver.add_constraint(s1, weight=1.0)
    solver.add_constraint(s2, weight=1.0)
    solver.add_constraint(s3, weight=1.0)

    x_init = np.array([2.0, 1.0])
    result = solver.solve(x_init, method="harmonic", max_iter=2000, tol=1e-8)

    print(f"結果成功: {result['success']}")
    print(f"反復回数: {result['iterations']}")
    print(f"調和点座標: {result['x']}")
    print(f"各超球制約との距離 (エラー): {result['constraint_errors']}")
    
    # 3つの中心 [0,0], [4,0], [2,3] の重心は [2.0, 1.0]
    # すべての円の半径が等しいため、重心が各円への射影の調和点となる
    assert np.allclose(result['x'], np.array([2.0, 1.0]), atol=1e-4)
    print("テスト2 成功!\n")

def test_10d_complex_constraints():
    print("=== テスト3: 10次元空間における複合制約 (Box, Hyperplane, Sphere) ===")
    dim = 10
    # 1. 境界制約: すべての次元で 0.0 <= x_i <= 1.0
    box = BoxConstraint(lower=np.zeros(dim), upper=np.ones(dim))
    
    # 2. 超平面制約: sum(x_i) = 3.0 (x の平均が 0.3)
    plane = Hyperplane(a=np.ones(dim), b=3.0)
    
    # 3. 超球制約: 中心 [0.5, 0.5, ...] から 半径 0.8 の超球内に収める
    sphere = Hypersphere(center=np.ones(dim)*0.5, radius=0.8)

    solver = MultiDimensionalGeometricSolver(dimension=dim)
    solver.add_constraint(box, weight=1.0)
    solver.add_constraint(plane, weight=1.0)
    solver.add_constraint(sphere, weight=1.0)

    # 初期値（すべて 0.9。これは境界内だが、合計は 9.0 になり超平面を満たさない）
    x_init = np.ones(dim) * 0.9
    result = solver.solve(x_init, method="pocs", max_iter=1000, tol=1e-8)

    print(f"結果成功: {result['success']}")
    print(f"反復回数: {result['iterations']}")
    print(f"収束座標 (最初の3次元分): {result['x'][:3]}")
    print(f"収束座標の合計値: {np.sum(result['x'])}")
    print(f"中心からの距離: {np.linalg.norm(result['x'] - np.ones(dim)*0.5)}")
    
    # すべての制約を満たしていることを検証
    # 1. Box
    assert np.all(result['x'] >= 0.0) and np.all(result['x'] <= 1.0)
    # 2. Hyperplane (誤差許容)
    assert np.isclose(np.sum(result['x']), 3.0, atol=1e-5)
    # 3. Sphere (中心からの距離が半径以下)
    assert np.linalg.norm(result['x'] - np.ones(dim)*0.5) <= 0.8 + 1e-5
    
    print("テスト3 成功!\n")

if __name__ == "__main__":
    test_3d_pocs_planes()
    test_2d_harmonic_spheres()
    test_10d_complex_constraints()
