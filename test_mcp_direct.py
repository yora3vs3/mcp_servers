#!/usr/bin/env python3
"""Test MCP server directly with HTTP requests"""

import requests
import json

MCP_URL = "http://127.0.0.1:9000/"
MODEL_ORIGIN = "http://127.0.0.1:8000"

def test_initialize():
    """Test initialize call"""
    print("\n" + "="*60)
    print("TEST 1: Initialize")
    print("="*60)
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize"
    }
    
    response = requests.post(MCP_URL, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_list_tools():
    """Test tools/list call"""
    print("\n" + "="*60)
    print("TEST 2: List Tools")
    print("="*60)
    
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    
    response = requests.post(MCP_URL, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_create_file():
    """Test create_file tool"""
    print("\n" + "="*60)
    print("TEST 3: Create File (Direct Tool Call)")
    print("="*60)
    
    payload = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "create_file",
            "arguments": {
                "filename": "mcp_direct_test.txt",
                "content": "Hello from direct MCP test!"
            }
        }
    }
    
    response = requests.post(MCP_URL, json=payload)
    print(f"Status: {response.status_code}")
    resp_json = response.json()
    print(f"Response: {json.dumps(resp_json, indent=2)}")
    
    # Verify file was created
    import os
    test_file = r"D:\Prj1.0\mcp_direct_test.txt"
    if os.path.exists(test_file):
        with open(test_file, 'r') as f:
            content = f.read()
        print(f"\n✅ FILE CREATED SUCCESSFULLY!")
        print(f"File path: {test_file}")
        print(f"File content: {content}")
        return True
    else:
        print(f"\n❌ FILE NOT FOUND: {test_file}")
        return False

def test_cors_headers():
    """Test CORS headers from model origin"""
    print("\n" + "="*60)
    print("TEST 4: CORS Headers (Simulating Model Origin)")
    print("="*60)
    
    payload = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "initialize"
    }
    
    headers = {
        "Origin": MODEL_ORIGIN,
        "Content-Type": "application/json"
    }
    
    response = requests.post(MCP_URL, json=payload, headers=headers)
    print(f"Status: {response.status_code}")
    
    # Check CORS headers in response
    cors_headers = {
        "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
        "Access-Control-Allow-Credentials": response.headers.get("Access-Control-Allow-Credentials"),
        "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
    }
    print(f"CORS Response Headers: {json.dumps(cors_headers, indent=2)}")
    
    if cors_headers["Access-Control-Allow-Origin"] == MODEL_ORIGIN:
        print(f"✅ CORS headers correct for origin: {MODEL_ORIGIN}")
        return True
    else:
        print(f"❌ CORS header mismatch!")
        return False

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# MCP SERVER DIRECT TEST")
    print("# Testing at: " + MCP_URL)
    print("#"*60)
    
    results = {
        "initialize": test_initialize(),
        "list_tools": test_list_tools(),
        "create_file": test_create_file(),
        "cors_headers": test_cors_headers(),
    }
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test}: {status}")
    
    all_passed = all(results.values())
    print("\n" + ("="*60))
    if all_passed:
        print("✅ ALL TESTS PASSED - MCP Server is working correctly!")
    else:
        print("❌ SOME TESTS FAILED - Check configuration")
    print("="*60)
