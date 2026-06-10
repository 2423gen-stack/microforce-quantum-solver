import os
import json
from mcp.server.fastmcp import FastMCP
from google import genai
from google.genai import types

# Create the Inference MCP Server Instance
# This is the wrapper for the Microforce Semantic Quantum Engine.
mcp_inference = FastMCP("microforce-quantum-solver")

@mcp_inference.tool()
async def quantum_solve(context_layers_json: str, goal: str) -> str:
    """
    Microforce Semantic Quantum Engine (Inference Tool).
    独立した複数の制約条件（JSON）を重ね合わせ、指定された目標（goal）に対する
    最適な解答をJSONとして結晶化（推論解決）します。
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return json.dumps({"error": "GEMINI_API_KEY environment variable is not set."}, ensure_ascii=False)

    client = genai.Client()

    prompt = f"""
    You are the Microforce Transparent Observation Engine.
    The following JSON data represents completely independent constraint layers.
    Superimpose these layers and crystallize ONE optimal solution that satisfies all conditions.
    
    [Goal]
    {goal}
    
    [Context Layers]
    {context_layers_json}
    
    [Output Format (JSON)]
    Output ONLY valid JSON representing the optimal solution. Do not include markdown formatting or extra text.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return response.text
    except Exception as e:
        return json.dumps({"error": f"Inference failed: {str(e)}"}, ensure_ascii=False)

if __name__ == "__main__":
    mcp_inference.run()
