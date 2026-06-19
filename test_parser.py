#!/usr/bin/env python3
"""
Test the agent's fallback tool parser for text-based tool calls
The model outputs text like: <|tool_call>call:create_file{content:"...",path:"..."}<tool_call|>
"""

import re
import json

def parse_text_tool_call(text):
    """From agent.py - fallback parser for text-based tool calls"""
    text = text.strip()
    print(f"Input text: {text[:100]}...")

    # create/edit file
    m = re.search(r'(create_file|edit_file)\("(.+?)","(.+?)"\)', text, re.DOTALL)
    if m:
        return m.group(1), {"filename": m.group(2), "content": m.group(3)}

    # read file
    m = re.search(r'read_file\("(.+?)"\)', text)
    if m:
        return "read_file", {"filename": m.group(1)}

    # list files
    if "list_files" in text:
        return "list_files", {"path": "."}

    # execute
    m = re.search(r'execute_command\("(.+?)"\)', text)
    if m:
        return "execute_command", {"command": m.group(1)}

    return None, None

def parse_zabibu_tool_call(text):
    """Enhanced parser for zabibu model's tool call format"""
    # Pattern: <|tool_call>call:create_file{content:"...",path:"..."}<tool_call|>
    # or: call:create_file{content:"...",path:"..."}
    
    pattern = r'(?:<\|)?tool_call\)?.*?call:(\w+)\{([^}]+)\}(?:(?:</tool_call>)?(?:\|>)?)'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if not match:
        print("No tool call pattern found")
        return None, None
    
    tool_name = match.group(1)
    args_str = match.group(2)
    
    print(f"Tool name: {tool_name}")
    print(f"Args string: {args_str}")
    
    # Parse key:value pairs from the args string
    # Handle both quoted and unquoted values
    args = {}
    
    # Try to extract key:"value" or key:value patterns
    param_pattern = r'(\w+):<\|"?([^,}]+?)<\|"?(?=[,}])|(\w+):<\|"?([^,}]+?)<\|"?$'
    
    # Simpler approach: look for content and path
    content_match = re.search(r'content:<\|"?([^,}]+?)<\|"?(?=[,}])', text)
    path_match = re.search(r'path:<\|"?([^,}]+?)<\|"?(?=[,}]|$)', text)
    
    if content_match:
        args["content"] = content_match.group(1)
    if path_match:
        args["path"] = path_match.group(1)
    
    # Fallback: try simple key:value parsing
    if not args:
        for part in args_str.split(','):
            part = part.strip()
            if ':' in part:
                key, val = part.split(':', 1)
                key = key.strip()
                val = val.strip().strip('"<|>').replace('<|"|>', '')
                args[key] = val
    
    print(f"Extracted args: {args}")
    
    # Map to standard filenames parameter
    if "path" in args and "filename" not in args:
        args["filename"] = args.pop("path")
    
    return tool_name, args

# Test cases
test_cases = [
    # Original format from agent.py
    'create_file("test.txt","Hello world")',
    'read_file("test.txt")',
    
    # Zabibu model format
    '<|tool_call>call:create_file{content:<|"|>This file was created by an LLM agent through MCP<|"|>,path:<|"|>llm_agent_test.txt<|"|>}<tool_call|>',
    'call:create_file{content:<|"|>Test content<|"|>,path:<|"|>test_file.txt<|"|>}',
]

print("="*60)
print("TEST: Tool Call Parsing")
print("="*60)

for i, test_input in enumerate(test_cases, 1):
    print(f"\n[Test {i}] Original Parser")
    print("-" * 40)
    tool_name, args = parse_text_tool_call(test_input)
    print(f"Result: {tool_name} -> {args}")
    
    # Try enhanced parser if original failed
    if not tool_name and 'call:' in test_input:
        print(f"\n[Test {i}] Enhanced Zabibu Parser")
        print("-" * 40)
        tool_name, args = parse_zabibu_tool_call(test_input)
        print(f"Result: {tool_name} -> {args}")

print("\n" + "="*60)
print("FINDINGS")
print("="*60)
print("""
✅ The agent.py parse_text_tool_call() works for standard format
⚠️  The zabibu model uses a special format with <|"|> markers
❌ Current agent.py parser doesn't handle zabibu format
✅ We can create an enhanced parser to handle it
""")
