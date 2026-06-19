#!/usr/bin/env python3
"""
Deep Diagnostic: Examine exact LLM output format
"""

import requests
import json

print("\n" + "="*70)
print("DEEP DIAGNOSTIC: LLM OUTPUT FORMAT ANALYSIS")
print("="*70)

# Request with tools
payload = {
    "model": "local",
    "messages": [
        {"role": "system", "content": "You are an agent with tool capabilities"},
        {"role": "user", "content": "Create a file named 'diagnostic_test.txt' with content 'test'"}
    ],
    "tools": [
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "Create a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {"type": "string"},
                        "content": {"type": "string"}
                    },
                    "required": ["filename", "content"]
                }
            }
        }
    ],
    "tool_choice": "auto",
    "max_tokens": 500
}

print("\nRequest:")
print(f"  URL: http://localhost:8000/v1/chat/completions")
print(f"  Model: {payload['model']}")
print(f"  Tools Provided: Yes (create_file)")
print(f"  Tool Choice: auto")

print("\n" + "-"*70)
print("Response Analysis:")
print("-"*70)

try:
    response = requests.post("http://localhost:8000/v1/chat/completions", json=payload, timeout=15)
    
    if response.status_code != 200:
        print(f"❌ HTTP Error {response.status_code}")
        print(response.text)
    else:
        full_response = response.json()
        
        # Pretty print full response
        print("\nFull Response JSON:")
        print(json.dumps(full_response, indent=2))
        
        # Analyze message structure
        msg = full_response["choices"][0]["message"]
        
        print("\n" + "-"*70)
        print("Message Structure Analysis:")
        print("-"*70)
        
        print(f"\nMessage keys: {list(msg.keys())}")
        
        for key, value in msg.items():
            if key == "content":
                print(f"\n  {key}:")
                print(f"    Type: {type(value)}")
                if value:
                    print(f"    Length: {len(str(value))} chars")
                    print(f"    Content preview:\n{value}")
                    
                    # Check for tool call patterns
                    if "tool_call" in str(value).lower():
                        print(f"\n    ⚠️  Contains 'tool_call' pattern")
                        if "<|tool_call>" in str(value):
                            print(f"    ✅ Uses <|tool_call> format")
                        if "call:" in str(value):
                            print(f"    ✅ Uses call: format")
                else:
                    print(f"    (empty)")
            
            elif key == "tool_calls":
                print(f"\n  {key}:")
                print(f"    Type: {type(value)}")
                if value:
                    print(f"    Count: {len(value)}")
                    for i, call in enumerate(value):
                        print(f"    Call {i+1}: {json.dumps(call, indent=6)}")
                else:
                    print(f"    (empty list)")
            
            else:
                print(f"\n  {key}: {value}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("CONCLUSION:")
print("="*70)
print("""
Based on the response structure, the LLM either:
1. Returns structured 'tool_calls' field (OpenAI format) ✅
2. Includes tool call text in 'content' field ✅
3. Doesn't support tools at all ❌

Check the output above to determine which path applies.
""")
