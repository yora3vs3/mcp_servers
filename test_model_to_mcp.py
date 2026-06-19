#!/usr/bin/env python3
"""
Test model-to-MCP integration
Simulates how the model would call MCP tools through HTTP
"""

import requests
import json
import time

MCP_URL = "http://127.0.0.1:9000/"
MODEL_URL = "http://127.0.0.1:8000/"
MODEL_ORIGIN = "http://127.0.0.1:8000"

def test_model_endpoint():
    """Check what's running on port 8000"""
    print("\n" + "="*60)
    print("STEP 1: Identify Model Endpoint")
    print("="*60)
    
    try:
        # Try common llama endpoints
        endpoints_to_test = [
            (f"{MODEL_URL}", "Root"),
            (f"{MODEL_URL}api/tags", "API Tags"),
            (f"{MODEL_URL}api/generate", "Generate Endpoint"),
            (f"{MODEL_URL}chat", "Chat"),
        ]
        
        for url, desc in endpoints_to_test:
            try:
                response = requests.get(url, timeout=2)
                print(f"✅ {desc}: Status {response.status_code}")
                if response.text[:100]:
                    print(f"   Response preview: {response.text[:100]}")
            except Exception as e:
                print(f"❌ {desc}: {str(e)}")
                
    except Exception as e:
        print(f"Error testing endpoints: {e}")

def test_model_to_mcp_flow():
    """
    Test the complete flow: Model requests MCP to create file
    This simulates what the model should do when instructed
    """
    print("\n" + "="*60)
    print("STEP 2: Simulate Model Calling MCP Server")
    print("="*60)
    
    # First, model would discover MCP tools
    print("\n[Model Action] Discovering MCP tools...")
    
    discovery_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list"
    }
    
    headers = {
        "Origin": MODEL_ORIGIN,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(MCP_URL, json=discovery_payload, headers=headers)
        if response.status_code == 200:
            tools = response.json()["result"]["tools"]
            print(f"✅ Discovered {len(tools)} tools from MCP server")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
        else:
            print(f"❌ Failed to list tools: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error discovering tools: {e}")
        return False
    
    # Now model calls create_file tool
    print("\n[Model Action] Calling create_file tool through MCP...")
    
    create_file_payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/call",
        "params": {
            "name": "create_file",
            "arguments": {
                "filename": "model_test.txt",
                "content": "Hello from LLM model via MCP server!"
            }
        }
    }
    
    try:
        response = requests.post(MCP_URL, json=create_file_payload, headers=headers)
        print(f"Response Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2)}")
        
        if response.status_code == 200 and "result" in result:
            print(f"✅ MCP create_file succeeded: {result['result']}")
            return True
        else:
            print(f"❌ MCP create_file failed")
            return False
            
    except Exception as e:
        print(f"❌ Error calling create_file: {e}")
        return False

def verify_file_creation():
    """Verify the file was actually created"""
    print("\n" + "="*60)
    print("STEP 3: Verify File Creation")
    print("="*60)
    
    import os
    test_file = r"D:\Prj1.0\model_test.txt"
    
    time.sleep(0.5)  # Give filesystem time to catch up
    
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            content = f.read()
        print(f"✅ FILE CREATED: {test_file}")
        print(f"Content: {content}")
        print(f"File size: {os.path.getsize(test_file)} bytes")
        return True
    else:
        print(f"❌ FILE NOT FOUND: {test_file}")
        return False

def test_cors_preflight():
    """Test CORS preflight request (OPTIONS)"""
    print("\n" + "="*60)
    print("STEP 4: Test CORS Preflight Request")
    print("="*60)
    
    headers = {
        "Origin": MODEL_ORIGIN,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type"
    }
    
    try:
        response = requests.options(MCP_URL, headers=headers, timeout=5)
        print(f"Status: {response.status_code}")
        
        cors_response = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
            "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
        }
        
        print(f"CORS Headers: {json.dumps(cors_response, indent=2)}")
        
        if response.headers.get("Access-Control-Allow-Origin") == MODEL_ORIGIN:
            print("✅ CORS preflight successful")
            return True
        else:
            print("❌ CORS preflight failed or incorrect origin")
            return False
            
    except Exception as e:
        print(f"❌ Error in preflight: {e}")
        return False

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# MODEL-TO-MCP INTEGRATION TEST")
    print("# Model: http://127.0.0.1:8000/")
    print("# MCP:   http://127.0.0.1:9000/")
    print("#"*60)
    
    results = {
        "model_endpoint": test_model_endpoint(),
        "cors_preflight": test_cors_preflight(),
        "model_to_mcp_flow": test_model_to_mcp_flow(),
        "file_creation": verify_file_creation(),
    }
    
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    
    for test, result in results.items():
        if result is not None:
            status = "✅" if result else "❌"
            print(f"{test}: {status}")
    
    print("\n" + "="*60)
    print("INTERPRETATION")
    print("="*60)
    
    if results.get("file_creation"):
        print("✅ SUCCESS: Model → MCP → File Creation works!")
        print("   The model can successfully call MCP tools to create files.")
    elif results.get("model_to_mcp_flow"):
        print("⚠️  PARTIAL: MCP responded but file not found.")
        print("   Check filesystem permissions or base directory.")
    else:
        print("❌ FAILED: Model cannot call MCP server properly.")
        print("   Check CORS, network connectivity, or MCP configuration.")
    
    print("="*60)
