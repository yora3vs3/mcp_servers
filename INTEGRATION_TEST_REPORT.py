#!/usr/bin/env python3
"""
COMPREHENSIVE INTEGRATION TEST REPORT
Testing Model (Port 8000) ↔ MCP Server (Port 9000) Integration
"""

import requests
import json
import os
from datetime import datetime

print("\n" + "#"*70)
print("# MODEL-TO-MCP INTEGRATION TEST REPORT")
print("# Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("#"*70)

print("""
SYSTEM OVERVIEW:
├── Port 8000: LLM Model (Zabibu-Fikra via Ollama/LM Studio)
│   ├── API Endpoint: http://localhost:8000/v1/chat/completions
│   ├── UI Frontend: http://127.0.0.1:8000/ (static web interface)
│   └── Tool Call Format: Text-based with <|tool_call> markers
│
├── Port 9000: MCP Server (FastAPI)
│   ├── Endpoint: http://127.0.0.1:9000/
│   ├── Protocol: JSON-RPC 2.0
│   ├── Tools: list_files, read_file, create_file, edit_file, execute_command
│   └── Base Directory: D:\\Prj1.0
│
└── Agent Logic (agent.py)
    ├── Queries LLM with tool definitions
    ├── Parses tool calls (supports text & structured formats)
    └── Forwards to MCP server for execution
""")

# ============================================================================
# TEST SUITE
# ============================================================================

test_results = {}

# TEST 1: MCP Server Health
print("\n" + "="*70)
print("TEST 1: MCP SERVER HEALTH CHECK")
print("="*70)

try:
    response = requests.post(
        "http://127.0.0.1:9000/",
        json={"jsonrpc": "2.0", "id": 1, "method": "initialize"},
        timeout=5
    )
    if response.status_code == 200:
        print("✅ MCP Server is running and responding")
        print(f"   Status: {response.status_code}")
        print(f"   Server Info: zabibu-fikra model on port 9000")
        test_results["MCP_Server_Health"] = True
    else:
        print(f"❌ MCP Server returned unexpected status: {response.status_code}")
        test_results["MCP_Server_Health"] = False
except Exception as e:
    print(f"❌ Cannot connect to MCP Server: {e}")
    test_results["MCP_Server_Health"] = False

# TEST 2: CORS Configuration
print("\n" + "="*70)
print("TEST 2: CORS CONFIGURATION")
print("="*70)

try:
    headers = {
        "Origin": "http://127.0.0.1:8000",
        "Access-Control-Request-Method": "POST",
    }
    response = requests.options("http://127.0.0.1:9000/", headers=headers, timeout=5)
    
    cors_origin = response.headers.get("Access-Control-Allow-Origin")
    cors_methods = response.headers.get("Access-Control-Allow-Methods")
    cors_creds = response.headers.get("Access-Control-Allow-Credentials")
    
    print(f"CORS Headers from MCP Server:")
    print(f"  Access-Control-Allow-Origin: {cors_origin}")
    print(f"  Access-Control-Allow-Methods: {cors_methods}")
    print(f"  Access-Control-Allow-Credentials: {cors_creds}")
    
    if cors_origin == "http://127.0.0.1:8000":
        print("✅ CORS properly configured for model origin")
        test_results["CORS_Config"] = True
    else:
        print(f"❌ CORS not properly configured for model")
        test_results["CORS_Config"] = False
        
except Exception as e:
    print(f"❌ CORS check failed: {e}")
    test_results["CORS_Config"] = False

# TEST 3: MCP Tools Availability
print("\n" + "="*70)
print("TEST 3: MCP TOOLS AVAILABILITY")
print("="*70)

try:
    response = requests.post(
        "http://127.0.0.1:9000/",
        json={"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        timeout=5
    )
    tools = response.json()["result"]["tools"]
    print(f"✅ Available Tools ({len(tools)} total):")
    for tool in tools:
        print(f"   - {tool['name']}: {tool['description']}")
    test_results["MCP_Tools_Available"] = True
except Exception as e:
    print(f"❌ Cannot list tools: {e}")
    test_results["MCP_Tools_Available"] = False

# TEST 4: Direct MCP File Creation (HTTP→MCP→Filesystem)
print("\n" + "="*70)
print("TEST 4: DIRECT MCP FILE CREATION")
print("="*70)

try:
    response = requests.post(
        "http://127.0.0.1:9000/",
        json={
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "create_file",
                "arguments": {
                    "filename": "integration_test_direct.txt",
                    "content": "Direct HTTP→MCP test successful"
                }
            }
        },
        timeout=5
    )
    
    if os.path.exists(r"D:\Prj1.0\integration_test_direct.txt"):
        print("✅ File created successfully via direct HTTP→MCP call")
        with open(r"D:\Prj1.0\integration_test_direct.txt") as f:
            content = f.read()
        print(f"   Content: {content}")
        test_results["Direct_HTTP_MCP"] = True
    else:
        print("❌ File not created")
        test_results["Direct_HTTP_MCP"] = False
        
except Exception as e:
    print(f"❌ Error: {e}")
    test_results["Direct_HTTP_MCP"] = False

# TEST 5: LLM API Connectivity
print("\n" + "="*70)
print("TEST 5: LLM API CONNECTIVITY")
print("="*70)

try:
    response = requests.post(
        "http://localhost:8000/v1/chat/completions",
        json={
            "model": "local",
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 50
        },
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        model_name = result.get("model", "unknown")
        print(f"✅ LLM API is responding")
        print(f"   Model: {model_name}")
        print(f"   Endpoint: http://localhost:8000/v1/chat/completions")
        test_results["LLM_API"] = True
    else:
        print(f"❌ LLM returned status {response.status_code}")
        test_results["LLM_API"] = False
        
except Exception as e:
    print(f"❌ Cannot connect to LLM API: {e}")
    test_results["LLM_API"] = False

# TEST 6: LLM Tool Understanding
print("\n" + "="*70)
print("TEST 6: LLM TOOL UNDERSTANDING")
print("="*70)

try:
    response = requests.post(
        "http://localhost:8000/v1/chat/completions",
        json={
            "model": "local",
            "messages": [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Create a file with name 'test' and content 'hello'"}
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "create_file",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "filename": {"type": "string"},
                                "content": {"type": "string"}
                            }
                        }
                    }
                }
            ],
            "tool_choice": "auto",
            "max_tokens": 300
        },
        timeout=10
    )
    
    if response.status_code == 200:
        msg = response.json()["choices"][0]["message"]
        
        if "tool_calls" in msg:
            print("✅ LLM returns structured tool_calls (JSON format)")
            print(f"   Tool calls: {len(msg['tool_calls'])}")
            test_results["LLM_Structured_Tools"] = True
        elif msg.get("content") and "tool_call" in msg["content"].lower():
            print("⚠️  LLM returns TEXT-BASED tool calls (not JSON)")
            print(f"   Tool format: <|tool_call>....<|tool_call|>")
            print(f"   Content preview: {msg['content'][:100]}...")
            test_results["LLM_Structured_Tools"] = False
            test_results["LLM_Text_Tools"] = True
        else:
            print("❌ LLM doesn't understand tools")
            test_results["LLM_Structured_Tools"] = False
            
    else:
        print(f"❌ LLM failed with status {response.status_code}")
        test_results["LLM_Structured_Tools"] = False
        
except Exception as e:
    print(f"❌ Error: {e}")
    test_results["LLM_Structured_Tools"] = False

# ============================================================================
# SUMMARY & RECOMMENDATIONS
# ============================================================================

print("\n" + "="*70)
print("SUMMARY")
print("="*70)

for test_name, passed in sorted(test_results.items()):
    if passed is not None:
        icon = "✅" if passed else "❌"
        print(f"{icon} {test_name}")

print("\n" + "="*70)
print("INTEGRATION VERDICT")
print("="*70)

all_critical = all([
    test_results.get("MCP_Server_Health"),
    test_results.get("CORS_Config"),
    test_results.get("LLM_API"),
])

if all_critical:
    print("✅ INFRASTRUCTURE: READY")
    print("   - MCP Server: Working")
    print("   - CORS: Configured")
    print("   - LLM API: Responding")
    
    if test_results.get("LLM_Structured_Tools"):
        print("\n✅ INTEGRATION: FULL SUPPORT")
        print("   LLM returns structured tool_calls")
        print("   → Ready to use standard agent.py directly")
        
    elif test_results.get("LLM_Text_Tools"):
        print("\n⚠️  INTEGRATION: PARTIAL (TEXT-BASED TOOLS)")
        print("   LLM returns text-based tool calls")
        print("   → Need to enhance agent.py parser for zabibu format:")
        print("      1. Update parse_text_tool_call() function")
        print("      2. Handle <|tool_call>....<|tool_call|> format")
        print("      3. Extract content and path from special markers")
        
    else:
        print("\n❌ LLM doesn't support tool calls")
else:
    print("❌ INFRASTRUCTURE: NOT READY")
    if not test_results.get("MCP_Server_Health"):
        print("   ❌ MCP Server not running (check port 9000)")
    if not test_results.get("CORS_Config"):
        print("   ❌ CORS not configured (check mcp_server.py)")
    if not test_results.get("LLM_API"):
        print("   ❌ LLM API not available (check port 8000/v1/chat/completions)")

print("\n" + "="*70)
print("NEXT STEPS")
print("="*70)

print("""
1. VERIFY ALL SERVICES ARE RUNNING:
   - MCP Server: uvicorn mcp_server:app --host 127.0.0.1 --port 9000
   - LLM Model: ollama serve OR LM Studio OR LocalAI on port 8000

2. TEST THROUGH LLAMA-UI:
   - Navigate to http://127.0.0.1:8000/
   - Send a message asking model to create a file
   - Example: "Create a file called 'ui_test.txt' with content 'Hello from UI'"

3. FOR FULL AGENT INTEGRATION:
   - Run: python agent.py "Create a file test.txt with hello"
   - The agent.py will:
     a) Send request to LLM
     b) Parse tool call response
     c) Forward to MCP server
     d) Execute and return result

4. IF TEXT-BASED TOOLS ISSUE OCCURS:
   - Update agent.py parse_text_tool_call() function
   - Use the enhanced parser from test_parser.py
   - Handle zabibu model's <|tool_call> format

5. VERIFY FILE CREATION:
   - Check D:\\Prj1.0\\ for created files
   - Verify content and permissions
""")

print("="*70)
print("FILES CREATED DURING THIS TEST:")
print("="*70)
test_files = [
    ("mcp_direct_test.txt", "Direct MCP HTTP test"),
    ("model_test.txt", "Model→MCP simulation test"),
    ("integration_test_direct.txt", "Integration test"),
]

for filename, description in test_files:
    filepath = f"D:\\Prj1.0\\{filename}"
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"✅ {filename} ({size} bytes) - {description}")
    else:
        print(f"❌ {filename} - NOT FOUND")

print("="*70)
