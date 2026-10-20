import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "profile.json"
STATIC_DIR = BASE_DIR / "static"

def load_profile_data() -> Dict[str, Any]:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

profile_data = load_profile_data()

app = FastAPI(
    title="Fadil Anwar - MCP Portfolio Server",
    description="Model Context Protocol (MCP) live portfolio server and interactive developer portfolio",
    version="1.0.0"
)

# CORS enabled for all origins (allow Claude Desktop, Cursor, Web UI, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MCP_PROTOCOL_VERSION = "2024-11-05"
SERVER_INFO = {
    "name": "fadil-anwar-portfolio-mcp",
    "version": "1.0.0"
}

# Tools, prompts, resources and the job-fit evaluator live in portfolio_core.py
from server.portfolio_core import (
    CONTACT_MESSAGES,
    TOOLS,
    PROMPTS,
    RESOURCES,
    load_profile_data,
    execute_tool,
    get_prompt_content,
    read_resource_content,
    get_seniority,
    server_instructions as _server_instructions,
)

# Core JSON-RPC 2.0 MCP Endpoint
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """
    Standard Model Context Protocol (MCP) JSON-RPC 2.0 endpoint.
    Compatible with Claude, Cursor, ChatGPT, and custom agent connectors.
    """
    start_time = time.time()
    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error: Invalid JSON"}
            }
        )

    # Handle notifications (no id)
    is_notification = "id" not in body
    rpc_id = body.get("id", None)
    method = body.get("method")
    params = body.get("params", {})

    if not method:
        return JSONResponse(
            status_code=400,
            content={
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32600, "message": "Invalid Request: missing method"}
            }
        )

    # Handshake & Protocol methods
    if method == "initialize":
        response_result = {
            "protocolVersion": MCP_PROTOCOL_VERSION,
            "capabilities": {
                "tools": {
                    "listChanged": False
                },
                "prompts": {
                    "listChanged": False
                },
                "resources": {
                    "subscribe": False,
                    "listChanged": False
                }
            },
            "serverInfo": SERVER_INFO,
            "instructions": _server_instructions()
        }

    elif method == "notifications/initialized":
        if is_notification:
            return Response(status_code=202)
        response_result = {}

    elif method == "ping":
        response_result = {}

    elif method == "tools/list":
        response_result = {
            "tools": TOOLS
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            tool_output = execute_tool(tool_name, arguments)
            response_result = {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(tool_output, indent=2) if not isinstance(tool_output, str) else tool_output
                    }
                ],
                "isError": False
            }
        except ValueError as e:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {"code": -32601, "message": str(e)}
                }
            )
        except Exception as e:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {"code": -32603, "message": f"Internal error during tool call: {str(e)}"}
                }
            )

    elif method == "prompts/list":
        response_result = {
            "prompts": PROMPTS
        }

    elif method == "prompts/get":
        prompt_name = params.get("name")
        arguments = params.get("arguments", {})
        try:
            prompt_res = get_prompt_content(prompt_name, arguments)
            response_result = prompt_res
        except ValueError as e:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {"code": -32601, "message": str(e)}
                }
            )

    elif method == "resources/list":
        response_result = {
            "resources": RESOURCES
        }

    elif method == "resources/read":
        uri = params.get("uri")
        try:
            content = read_resource_content(uri)
            response_result = {
                "contents": [
                    {
                        "uri": uri,
                        "mimeType": "text/markdown",
                        "text": content
                    }
                ]
            }
        except ValueError as e:
            return JSONResponse(
                content={
                    "jsonrpc": "2.0",
                    "id": rpc_id,
                    "error": {"code": -32602, "message": str(e)}
                }
            )

    else:
        return JSONResponse(
            content={
                "jsonrpc": "2.0",
                "id": rpc_id,
                "error": {"code": -32601, "message": f"Method '{method}' not implemented"}
            }
        )

    duration_ms = round((time.time() - start_time) * 1000, 2)
    response_payload = {
        "jsonrpc": "2.0",
        "id": rpc_id,
        "result": response_result,
        "_meta": {
            "durationMs": duration_ms,
            "server": SERVER_INFO["name"]
        }
    }

    return JSONResponse(content=response_payload)


# SSE (Server-Sent Events) Endpoint for SSE-based MCP Clients
@app.get("/sse")
async def mcp_sse_endpoint():
    """
    Standard MCP SSE Transport endpoint.
    Sends initial endpoint discovery and protocol initialization event.
    """
    async def event_generator():
        # Event 1: endpoint declaration
        endpoint_event = {
            "type": "endpoint",
            "url": "/mcp"
        }
        yield f"event: endpoint\ndata: {json.dumps(endpoint_event)}\n\n"
        
        # Event 2: ready status
        status_event = {
            "status": "ready",
            "server": SERVER_INFO,
            "protocol": MCP_PROTOCOL_VERSION
        }
        yield f"event: status\ndata: {json.dumps(status_event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# REST API Endpoints for Web Dashboard
@app.get("/api/health")
def api_health():
    return {
        "status": "online",
        "server": SERVER_INFO["name"],
        "protocolVersion": MCP_PROTOCOL_VERSION,
        "timestamp": time.time(),
        "toolsCount": len(TOOLS),
        "promptsCount": len(PROMPTS),
        "resourcesCount": len(RESOURCES)
    }

@app.get("/api/profile")
def api_profile():
    return load_profile_data()

@app.get("/api/tools")
def api_tools():
    return {"tools": TOOLS, "prompts": PROMPTS}

class ContactRequest(BaseModel):
    name: str = Field(..., min_length=1)
    email: str = Field(..., min_length=3)
    subject: Optional[str] = "Portfolio Outreach"
    message: str = Field(..., min_length=1)

@app.post("/api/contact")
def api_contact(body: ContactRequest):
    data = load_profile_data()
    msg = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "name": body.name,
        "email": body.email,
        "subject": body.subject,
        "message": body.message
    }
    CONTACT_MESSAGES.append(msg)
    return {
        "success": True,
        "message": f"Message received, {body.name}! Fadil will respond soon.",
        "recipient": data["personal"]["email"]
    }

# Mount static directory for the portfolio website
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "Fadil Anwar MCP Portfolio Server is running. Visit /mcp for JSON-RPC protocol."}
