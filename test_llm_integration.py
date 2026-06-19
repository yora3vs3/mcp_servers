#!/usr/bin/env python3
"""
Test the complete flow:
1. LLM API (port 8000/v1/chat/completions)
2. Agent logic that parses tool calls
3. MCP server handling
"""

import requests
import json

LLM_API = "http://localhost:8000/v1/chat/completions"
MCP_SERVER = "http://127.0.0.1:9000/"

def test_llm_api_endpoint():
    """Test if LLM API endpoint is available"""
    print("\n" + "="*60)
    print("TEST 1: LLM API Endpoint")
    print("="*60)
    
    payload = {
        "model": "local",
        "messages": [
            {"role": "user", "content": "Hello, who are you?"}
        ],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(LLM_API, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ LLM API is responsive")
            print(f"Response: {json.dumps(result, indent=2)[:300]}...")
            return True
        else:
            print(f"❌ LLM API returned {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to LLM API: {LLM_API}")
        print("   Note: The model server might not be running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_llm_with_tools():
    """Test if LLM can accept tool definitions"""
    print("\n" + "="*60)
    print("TEST 2: LLM with Tool Definitions")
    print("="*60)
    
    tools = [
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
    ]
    
    payload = {
        "model": "local",
        "messages": [
            {
                "role": "system",
                "content": "You are a coding assistant. Use the create_file tool to create files when asked."
            },
            {
                "role": "user",
                "content": "Create a file called test_llm.txt with the content 'Created by LLM'"
            }
        ],
        "tools": tools,
        "tool_choice": "auto",
        "max_tokens": 200
    }
    
    try:
        response = requests.post(LLM_API, json=payload, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            msg = result["choices"][0]["message"]
            
            print(f"✅ LLM accepts tools parameter")
            
            # Check if LLM returned tool calls
            if "tool_calls" in msg:
                print(f"✅ LLM returned tool_calls: {len(msg['tool_calls'])} calls")
                for call in msg["tool_calls"]:
                    print(f"   - {call['function']['name']}: {call['function']['arguments']}")
                return True
            else:
                print(f"⚠️  LLM did NOT return tool_calls")
                print(f"Response content: {msg['content'][:200] if msg.get('content') else 'None'}")
                return False
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to LLM API")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_full_agent_flow():
    """Test the full agent-MCP-LLM flow"""
    print("\n" + "="*60)
    print("TEST 3: Full Agent Flow (LLM → Tool Call → MCP → File Creation)")
    print("="*60)
    
    # Step 1: Query LLM with tool capability
    print("\n[Step 1] Query LLM with tool capability...")
    
    tools = [
        {
            "type": "function",
            "function": {
                "name": "create_file",
                "description": "Create a file with content",
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
    ]
    
    payload = {
        "model": "local",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant with access to file creation tools. When asked to create a file, use the create_file tool."
            },
            {
                "role": "user",
                "content": "Create a test file called 'llm_agent_test.txt' with the content 'This file was created by an LLM agent through MCP'"
            }
        ],
        "tools": tools,
        "tool_choice": "auto",
        "max_tokens": 300
    }
    
    try:
        llm_response = requests.post(LLM_API, json=payload, timeout=10)
        
        if llm_response.status_code != 200:
            print(f"❌ LLM API failed: {llm_response.status_code}")
            return False
        
        llm_result = llm_response.json()
        msg = llm_result["choices"][0]["message"]
        
        if "tool_calls" not in msg:
            print(f"⚠️  LLM did not generate tool calls")
            print(f"Response: {msg.get('content', 'No content')[:200]}")
            return False
        
        # Step 2: Extract tool call and forward to MCP
        print(f"[Step 2] LLM returned {len(msg['tool_calls'])} tool call(s)")
        
        tool_call = msg["tool_calls"][0]
        tool_name = tool_call["function"]["name"]
        tool_args = json.loads(tool_call["function"]["arguments"])
        
        print(f"Tool: {tool_name}")
        print(f"Args: {json.dumps(tool_args, indent=2)}")
        
        # Step 3: Forward to MCP server
        print(f"\n[Step 3] Forwarding to MCP server...")
        
        mcp_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": tool_args
            }
        }
        
        mcp_response = requests.post(MCP_SERVER, json=mcp_payload, timeout=10)
        
        if mcp_response.status_code != 200:
            print(f"❌ MCP failed: {mcp_response.status_code}")
            return False
        
        mcp_result = mcp_response.json()
        print(f"✅ MCP result: {mcp_result['result']}")
        
        # Verify file creation
        import os
        test_file = r"D:\Prj1.0\llm_agent_test.txt"
        
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            print(f"✅ FILE CREATED: {test_file}")
            print(f"Content: {content}")
            return True
        else:
            print(f"❌ File not found: {test_file}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# LLM + MCP INTEGRATION TEST")
    print("# LLM API: " + LLM_API)
    print("# MCP:     " + MCP_SERVER)
    print("#"*60)
    
    results = {
        "llm_api_endpoint": test_llm_api_endpoint(),
        "llm_with_tools": test_llm_with_tools(),
        "full_agent_flow": test_full_agent_flow(),
    }
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for test, passed in results.items():
        if passed is not None:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{test}: {status}")
    
    print("\n" + "="*60)
    print("DIAGNOSTICS")
    print("="*60)
    
    if not results["llm_api_endpoint"]:
        print("⚠️  LLM API is NOT available on port 8000/v1/chat/completions")
        print("    Check if your model server (LM Studio/Ollama/LocalAI) is running")
        print("    This is REQUIRED for the agent to work")
    
    elif not results["llm_with_tools"]:
        print("⚠️  LLM accepts connections but does not support tool calls")
        print("    Your model might not support function calling")
        print("    Try a model that supports tool/function calling")
    
    elif results["full_agent_flow"]:
        print("✅ FULL INTEGRATION SUCCESSFUL!")
        print("   The LLM → MCP → File creation flow works perfectly!")
    
    print("="*60)
