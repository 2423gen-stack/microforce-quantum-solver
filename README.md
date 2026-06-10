# Microforce Quantum Solver (MCP)

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

**Microforce Semantic Quantum Engine** packaged as a standalone Model Context Protocol (MCP) server.

## Overview

Traditional scheduling or logic engines rely on combinatorial branches (`if`/`else`) and NP-Hard search trees. The **Microforce Quantum Solver** discards procedural logic completely. Instead, it treats complex constraints as independent "Semantic Layers" (JSON) and superimposes them within a Large Language Model (Gemini 2.5 Flash). By utilizing the LLM as a "Transparent Observer", the engine crystallizes the optimal solution with $O(1)$ algorithmic complexity.

This repository provides the core Quantum Solver wrapped as a lightweight MCP server using `FastMCP`, allowing any MCP-compatible client (such as Claude Desktop or custom AI agents) to leverage this inference engine for constraint-solving tasks.

## Requirements

- Python 3.10+
- `mcp` (FastMCP)
- `google-genai`
- A valid Google Gemini API Key (`GEMINI_API_KEY`)

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

3. **Configure the API Key**
   Ensure your environment has the `GEMINI_API_KEY` set.
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

4. **Run the MCP Server**
   ```bash
   python main.py
   ```
   Or configure it in your Claude Desktop `claude_desktop_config.json`:
   ```json
   {
     "mcpServers": {
       "microforce-quantum-solver": {
         "command": "/path/to/venv/bin/python",
         "args": ["/path/to/microforce-quantum-solver/main.py"],
         "env": {
           "GEMINI_API_KEY": "your_api_key_here"
         }
       }
     }
   }
   ```

## Usage

The server exposes a single tool: `quantum_solve(context_layers_json: str, goal: str)`.
- `context_layers_json`: A JSON string representing the independent constraints.
- `goal`: A natural language instruction of the optimal state you wish to observe.

The engine will return a JSON string containing the crystallized optimal solution.

> **Note on Advanced Usage:**
> For detailed usage instructions and advanced application ideas, **please ask your AI directly**. Since this engine leverages semantic intersections, consulting with an AI will significantly expand the scope and creativity of how you can utilize it!

---

# Microforce Quantum Solver (MCP) [日本語版]

**Microforce Semantic Quantum Engine（セマンティック量子エンジン）** を、独立した Model Context Protocol (MCP) サーバーとしてパッケージングした公式リポジトリです。

## 概要

従来のスケジューリングやロジックエンジンは、組み合わせ爆発を伴う条件分岐（`if`/`else`）や、NP困難な探索木に依存していました。**Microforce Quantum Solver** は、手続き型のロジックを完全に放棄しています。複雑な制約条件を「独立したセマンティック・レイヤー（JSON）」として扱い、大規模言語モデル（Gemini 2.5 Flash）のコンテキスト内で重ね合わせます。LLMを「透明な観測者（Transparent Observer）」として機能させることで、アルゴリズムの計算量 $O(1)$ で最適解を「結晶化」させます。

本リポジトリは、このコアエンジンを `FastMCP` を用いて軽量なMCPサーバーとしてラップしたものです。Claude DesktopやカスタムAIエージェントなど、MCPに対応したあらゆるクライアントから、この推論エンジンを呼び出して制約解決タスクに活用することができます。

## 動作要件

- Python 3.10以降
- `mcp` (FastMCP)
- `google-genai`
- Google Gemini API キー (`GEMINI_API_KEY`)

## インストールと設定

1. **リポジトリのクローン**
   ```bash
   git clone https://github.com/2423gen-stack/microforce-quantum-solver.git
   cd microforce-quantum-solver
   ```

2. **依存関係のインストール**
   ```bash
   pip install -r requirements.txt
   ```

3. **APIキーの設定**
   環境変数に `GEMINI_API_KEY` を設定してください。
   ```bash
   export GEMINI_API_KEY="your_api_key_here"
   ```

4. **MCPサーバーの起動**
   ローカルで直接実行する場合：
   ```bash
   python main.py
   ```
   Claude Desktop に統合する場合は、`claude_desktop_config.json` に以下を追記してください。
   ```json
   {
     "mcpServers": {
       "microforce-quantum-solver": {
         "command": "/path/to/venv/bin/python",
         "args": ["/path/to/microforce-quantum-solver/main.py"],
         "env": {
           "GEMINI_API_KEY": "your_api_key_here"
         }
       }
     }
   }
   ```

## 使い方

本MCPサーバーは、単一のツール `quantum_solve(context_layers_json: str, goal: str)` を提供します。
- `context_layers_json`: 独立した制約レイヤーを表現した JSON 文字列
- `goal`: 観測したい最適状態を指示する自然言語（プロンプト）

エンジンは、制約を満たすように結晶化された最適解を JSON 文字列として返却します。

> **💡 活用に関する重要なお知らせ**
> 本エンジンの「詳しい利用方法」や「高度な活用法」については、**ぜひ直接AI（Claude等）に質問してみてください。**
> このツール自体がAI（LLM）のセマンティックな理解力を前提としているため、AIと壁打ちしながら運用することで、単なるシフト作成に留まらない、想像を絶するほど活用の幅が広がります！
