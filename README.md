# Microforce Quantum Solver v2

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

**Microforce Multidimensional Geometric Solver** for deterministic constraint-solving and projection onto convex sets (POCS).

## Overview

Traditional scheduling or logic engines rely on combinatorial branches (`if`/`else`) and NP-Hard search trees. The **Microforce Quantum Solver v2** discards non-deterministic and heavy procedural search algorithms. 

Instead, it separates the optimization process into two steps:
1. **Geometric Translation (LLM Compiler)**: The engine translates complex constraints written in Markdown or JSON into geometric primitives (Hyperplanes, Half-spaces, Box constraints, Hyperspheres) in a multidimensional vector space $\mathbb{R}^N$.
2. **Deterministic Solution**: A fast, local linear-algebra solver uses **POCS (Projection onto Convex Sets)** or **Harmonic Projection (Weighted Average)** to converge on the mathematically optimal solution (the intersection/centroid) in a few iterations without randomness or search-space explosion.

---

## Core Components

- **Hyperplane**: $\mathbf{a}^T \mathbf{x} = b$
- **HalfSpace**: $\mathbf{a}^T \mathbf{x} \le b$
- **BoxConstraint**: $\mathbf{l} \le \mathbf{x} \le \mathbf{u}$
- **Hypersphere**: $\|\mathbf{x} - \mathbf{c}\|_2 \le R$
- **AffineSubspace**: $\mathbf{A}\mathbf{x} = \mathbf{b}$
- **MultiDimensionalGeometricSolver**: A state-vector optimization engine that handles sequential projection (POCS) and weighted average projection (Harmonic / centroid solving).

## Requirements

- Python 3.10+
- NumPy

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/2423gen-stack/microforce-quantum-solver.git
   cd microforce-quantum-solver
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage & Verification

You can verify the mathematical soundness of the solver by running the pure geometric tests:
```bash
python3 test_geometry.py
```

---

# Microforce Quantum Solver v2 [日本語版]

**多次元幾何オブジェクトと直交射影法（POCS / Harmonic）** を用いて、確定的かつ超高速に多変数制約充足問題を解くための幾何代数演算ソルバーです。

## 概要

従来の最適化エンジンやロジックエンジンは、組み合わせ爆発を伴う条件分岐（`if`/`else`）や、NP困難な探索木、メタヒューリスティクス（焼きなまし等）に依存していました。**Microforce Quantum Solver v2** は、探索ベースの手続き型ロジックを完全に排除します。

本アーキテクチャは最適化を以下の2ステップに分離して解決します。
1. **幾何コンパイル (LLM Compiler)**: 自然言語やJSON形式の制約情報を、多次元ベクトル空間 $\mathbb{R}^N$ における幾何プリミティブ（超平面、半空間、境界ボックス、超球など）の方程式・領域に翻訳します。
2. **確定的幾何解決 (Deterministic Solver)**: 構築された幾何プリミティブ群に対し、**交互射影法 (POCS)** または **調和平均射影 (Harmonic)** を用いて、すべての制約を満たす積集合（または最も葛藤の少ない調和点）へ数回のベクトル演算のみで決定論的に収束させます。

---

## 提供される幾何プリミティブ

*   **Hyperplane (超平面)**: $\mathbf{a}^T \mathbf{x} = b$
*   **HalfSpace (半空間 / 不等式境界)**: $\mathbf{a}^T \mathbf{x} \le b$
*   **BoxConstraint (境界ボックス)**: $\mathbf{l} \le \mathbf{x} \le \mathbf{u}$
*   **Hypersphere (超球)**: $\|\mathbf{x} - \mathbf{c}\|_2 \le R$
*   **AffineSubspace (アフィン部分空間)**: $\mathbf{A}\mathbf{x} = \mathbf{b}$
*   **MultiDimensionalGeometricSolver**: 上記制約オブジェクトを束ね、交互射影および調和平均によって最適解を「結晶化」させるソルバー本体。

## 動作要件

- Python 3.10以降
- NumPy

## クイックスタート & 動作検証

以下のコマンドを実行することで、純粋幾何学的な制約充足問題（3次元平面交点、2次元超球調和点、10次元複合制約）に対する確定的かつ高速な収束テストを検証できます。
```bash
python3 test_geometry.py
```
