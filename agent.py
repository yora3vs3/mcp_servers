import requests
import json
import os
import subprocess
import re

LLM_URL = "http://localhost:8000/v1/chat/completions"

# ✅ tools definition (for LLM)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "parameters": {"type": "object", "properties": {"filename": {"type": "string"}}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_command",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string"}},
                "required": ["command"]
            }
        }
    }
]

# ✅ LOCAL tool execution (NO MCP)
def call_tool(name, args):
    try:
        if name == "list_files":
            path = args.get("path", ".")
            return os.listdir(path)

        elif name == "read_file":
            with open(args["filename"], "r", encoding="utf-8") as f:
                return f.read()

        elif name in ["create_file", "edit_file"]:
            with open(args["filename"], "w", encoding="utf-8") as f:
                f.write(args["content"])
            return f"{args['filename']} written successfully"

        elif name == "execute_command":
            return subprocess.getoutput(args["command"])

    except Exception as e:
        return str(e)


# ✅ fallback parser (for GGUF models that don't format tools properly)
def parse_text_tool_call(text):
    text = text.strip()

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


# ✅ main agent
def run_agent(prompt):
    messages = [
        {
            "role": "system",
            "content": """
You are an autonomous coding agent.

RULES:
- ALWAYS use tools for actions
- NEVER pretend you created files
- Use create_file, read_file, execute_command properly
- Keep outputs SHORT
"""
        },
        {"role": "user", "content": prompt}
    ]

    while True:
        response = requests.post(
            LLM_URL,
            json={
                "model": "local",
                "messages": messages,
                "tools": TOOLS,
                "tool_choice": "auto",
                "max_tokens": 200
            }
        ).json()

        msg = response["choices"][0]["message"]

        # ✅ structured tool call
        if "tool_calls" in msg:
            for t in msg["tool_calls"]:
                name = t["function"]["name"]
                args = json.loads(t["function"]["arguments"])

                print(f"\n[TOOL] {name} → {args}")
                result = call_tool(name, args)

                messages.append(msg)
                messages.append({"role": "tool", "content": str(result)})

        else:
            # ✅ fallback parsing
            content = msg.get("content", "")
            name, args = parse_text_tool_call(content)

            if name:
                print(f"\n[PARSED] {name} → {args}")
                result = call_tool(name, args)

                messages.append(msg)
                messages.append({"role": "tool", "content": str(result)})

            else:
                print("\n✅ FINAL OUTPUT:\n")
                print(content)
                break


# ✅ RUN
if __name__ == "__main__":
    run_agent(
        "List files. Create sys_info.py that prints Python version. Then run it."
    )