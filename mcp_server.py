from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess

app = FastAPI()

# ✅ CORS (required for Open WebUI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Fixed working directory
BASE_DIR = r"D:\Prj1.0"


# ✅ Safe path (prevents escaping base dir)
def safe_path(path: str):
    full_path = os.path.abspath(os.path.join(BASE_DIR, path))

    # normalize for Windows case sensitivity
    if not full_path.lower().startswith(BASE_DIR.lower()):
        raise Exception("Access outside allowed directory")

    return full_path


@app.post("/")
async def handle_rpc(payload: dict):
    try:
        method = payload.get("method")
        params = payload.get("params", {})
        rpc_id = payload.get("id", 1)

        # ✅ INITIALIZE (correct MCP spec)
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "mcp-server",
                        "version": "2.1"
                    },
                    "capabilities": {
                        "tools": {
                            "listChanged": False
                        }
                    }
                }
            }

        # ✅ LIST TOOLS
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "tools": [
                        {
                            "name": "list_files",
                            "description": "List files in directory",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string"}
                                }
                            }
                        },
                        {
                            "name": "read_file",
                            "description": "Read file content",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "filename": {"type": "string"}
                                },
                                "required": ["filename"]
                            }
                        },
                        {
                            "name": "create_file",
                            "description": "Create a file",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "filename": {"type": "string"},
                                    "content": {"type": "string"}
                                },
                                "required": ["filename", "content"]
                            }
                        },
                        {
                            "name": "edit_file",
                            "description": "Edit a file",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "filename": {"type": "string"},
                                    "content": {"type": "string"}
                                },
                                "required": ["filename", "content"]
                            }
                        },
                        {
                            "name": "execute_command",
                            "description": "Execute shell command",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "command": {"type": "string"}
                                },
                                "required": ["command"]
                            }
                        }
                    ]
                }
            }

        # ✅ TOOL EXECUTION (STRICT + SAFE)
        if method == "tools/call":
            name = params.get("name")
            args = params.get("arguments", {})

            print(f"\n[TOOL CALL] {name} → {args}")

            try:
                # ✅ LIST FILES
                if name == "list_files":
                    target = safe_path(args.get("path", ""))
                    result = {
                        "cwd": BASE_DIR,
                        "files": os.listdir(target)
                    }

                # ✅ READ FILE
                elif name == "read_file":
                    target = safe_path(args["filename"])

                    if not os.path.exists(target):
                        raise Exception("File does not exist")

                    with open(target, "r", encoding="utf-8") as f:
                        result = f.read()

                # ✅ CREATE FILE (FIXED)
                elif name == "create_file":
                    target = safe_path(args["filename"])
                    content = args.get("content", "")

                    # ✅ FIX: enforce content
                    if not content.strip():
                        content = "File created (no content provided)."

                    os.makedirs(os.path.dirname(target), exist_ok=True)

                    with open(target, "w", encoding="utf-8") as f:
                        f.write(content)

                    if not os.path.exists(target):
                        raise Exception("File creation failed")

                    result = f"Created: {target}"

                # ✅ EDIT FILE
                elif name == "edit_file":
                    target = safe_path(args["filename"])
                    content = args.get("content", "")

                    if not content.strip():
                        raise Exception("Cannot overwrite with empty content")

                    with open(target, "w", encoding="utf-8") as f:
                        f.write(content)

                    result = f"Updated: {target}"

                # ✅ EXECUTE COMMAND
                elif name == "execute_command":
                    result = subprocess.getoutput(args["command"])

                else:
                    raise Exception(f"Unknown tool: {name}")

            except Exception as e:
                result = f"ERROR: {str(e)}"

            print(f"[RESULT] {result}")

            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": result
            }

        # ✅ UNKNOWN METHOD
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {
                "code": -32601,
                "message": "Method not found"
            }
        }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": payload.get("id", 1),
            "error": {
                "code": -32000,
                "message": str(e)
            }
        }