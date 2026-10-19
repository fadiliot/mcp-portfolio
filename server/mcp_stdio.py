#!/usr/bin/env python3
"""
Standard Model Context Protocol (MCP) stdio Transport Server.
Directly compatible with Claude Desktop, Cursor, and any local stdio MCP client.
"""
import sys
import json
from pathlib import Path

# Set up paths
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from server.mcp_server import (
    load_profile_data,
    execute_tool,
    get_prompt_content,
    read_resource_content,
    TOOLS,
    PROMPTS,
    RESOURCES,
    MCP_PROTOCOL_VERSION,
    SERVER_INFO
)

# Reconfigure utf-8
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stdin.encoding != 'utf-8':
    try:
        sys.stdin.reconfigure(encoding='utf-8')
    except Exception:
        pass

def handle_request(req: dict) -> dict:
    rpc_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if not method:
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {"code": -32600, "message": "Invalid Request: missing method"}
        }

    if method == "initialize":
        data = load_profile_data()
        name = data.get("personal", {}).get("name", "Fadil Anwar")
        title = data.get("personal", {}).get("title", "AI Engineer")
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "result": {
                "protocolVersion": MCP_PROTOCOL_VERSION,
                "capabilities": {
                    "tools": {"listChanged": False},
                    "prompts": {"listChanged": False},
                    "resources": {"subscribe": False, "listChanged": False}
                },
                "serverInfo": SERVER_INFO,
                "instructions": f"This is the live Model Context Protocol (MCP) portfolio server for {name}, {title}. Use available tools to screen qualifications, inspect work history, evaluate job fit, or initiate contact."
            }
        }

    elif method == "notifications/initialized":
        return None

    elif method == "ping":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {}}

    elif method == "tools/list":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {"tools": TOOLS}}

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            tool_output = execute_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(tool_output, indent=2) if not isinstance(tool_output, str) else tool_output
                        }
                    ],
                    "isError": False
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32603, "message": str(e)}
            }

    elif method == "prompts/list":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {"prompts": PROMPTS}}

    elif method == "prompts/get":
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            prompt_res = get_prompt_content(prompt_name, arguments)
            return {"jsonrpc": "2.0", "id": rpc_id, "result": prompt_res}
        except Exception as e:
            return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32601, "message": str(e)}}

    elif method == "resources/list":
        return {"jsonrpc": "2.0", "id": rpc_id, "result": {"resources": RESOURCES}}

    elif method == "resources/read":
        uri = params.get("uri")
        try:
            content = read_resource_content(uri)
            return {
                "jsonrpc": "2.0",
                "id": rpc_id,
                "result": {
                    "contents": [{"uri": uri, "mimeType": "text/markdown", "text": content}]
                }
            }
        except Exception as e:
            return {"jsonrpc": "2.0", "id": rpc_id, "error": {"code": -32602, "message": str(e)}}

    else:
        return {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "error": {"code": -32601, "message": f"Method '{method}' not implemented"}
        }

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            res = handle_request(req)
            if res is not None:
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()
        except json.JSONDecodeError:
            err = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }
            sys.stdout.write(json.dumps(err) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
