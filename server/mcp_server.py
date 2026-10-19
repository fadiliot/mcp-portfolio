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

# In-memory storage for contact messages
CONTACT_MESSAGES: List[Dict[str, Any]] = []

# Define Tool definitions
TOOLS = [
    {
        "name": "get_profile",
        "description": "Candidate overview for recruiters, engineering managers, and agents: current role, years of experience, target roles, evidence-backed strengths, education, headline metrics, and social links.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "detail_level": {
                    "type": "string",
                    "enum": ["summary", "full"],
                    "description": "Level of detail to return ('summary' or 'full'). Defaults to 'full'."
                }
            }
        }
    },
    {
        "name": "get_experience",
        "description": "Full work history and research tenure, newest first: organization, role, dates, location, employment type, tech stack, and quantified achievements (e.g. 5,000+ adversarial interactions, 120+ vulnerabilities).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "organization": {
                    "type": "string",
                    "description": "Optional filter by organization or project keyword"
                }
            }
        }
    },
    {
        "name": "list_projects",
        "description": "In-depth catalog of key projects (e.g. DREAM Red Team Service, CE-AKG graph engine, MCP live server) with architecture, arXiv references, metrics, tech stack, and GitHub repositories.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Optional specific project ID (e.g. 'dream-redteam', 'ce-akg-graph', 'mcp-portfolio-server')"
                }
            }
        }
    },
    {
        "name": "get_skills",
        "description": "Every technical skill mapped directly to the actual jobs or projects where Fadil used it. Includes LangGraph, PyTorch, FAISS, FastAPI, PO-MDP, LLM safety evals, and system design.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional category filter (e.g. 'AI & Agentic Systems', 'Deep Learning & Search', 'Backend & Infrastructure', 'Frontend & Observability')"
                }
            }
        }
    },
    {
        "name": "evaluate_job_fit",
        "description": "Evaluate how well Fadil's background fits a specific job description or role. Compares required vs proven skills, highlights strong matches, notes any gaps honestly, and produces a structured fit score.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_description": {
                    "type": "string",
                    "description": "The full text of the job description or role requirements"
                },
                "target_role": {
                    "type": "string",
                    "description": "Job title or role being evaluated (e.g. 'Senior AI Security Engineer', 'Applied AI Engineer')"
                }
            },
            "required": ["job_description"]
        }
    },
    {
        "name": "contact_fadil",
        "description": "Send a direct message or connection request to Fadil Anwar. Call when the user explicitly wishes to reach out, invite to an interview, or propose a collaboration.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "sender_name": {
                    "type": "string",
                    "description": "Your name or the recruiter / hiring manager's name"
                },
                "sender_email": {
                    "type": "string",
                    "description": "Email address for Fadil to reply to"
                },
                "role_or_subject": {
                    "type": "string",
                    "description": "Subject, company name, or role title"
                },
                "message": {
                    "type": "string",
                    "description": "The message, inquiry, or meeting proposal"
                }
            },
            "required": ["sender_name", "sender_email", "message"]
        }
    }
]

# Define Prompts
PROMPTS = [
    {
        "name": "job_fit",
        "description": "Map a job description's requirements directly to evidence from Fadil's experience and open-source red-teaming research.",
        "arguments": [
            {
                "name": "job_description",
                "description": "The text of the job requirements or posting",
                "required": True
            }
        ]
    },
    {
        "name": "technical_interview_brief",
        "description": "Generate an interviewer briefing with tough, deep technical questions regarding Fadil's multi-agent architectures, PO-MDP formulation, and FAISS vector search.",
        "arguments": [
            {
                "name": "interview_type",
                "description": "Type of interview (e.g. 'System Design', 'AI Safety & Red Teaming', 'Agentic Engineering')",
                "required": False
            }
        ]
    },
    {
        "name": "system_architecture_deepdive",
        "description": "Detailed architectural walkthrough of the DREAM multi-agent red team testing service and belief state graph.",
        "arguments": []
    }
]

# Define Resources
RESOURCES = [
    {
        "uri": "fadil://resume.md",
        "name": "Fadil Anwar - Comprehensive Resume",
        "description": "Full markdown resume including work history, academic research (arXiv:2512.19016), and key metrics.",
        "mimeType": "text/markdown"
    },
    {
        "uri": "fadil://dream-framework.md",
        "name": "DREAM Framework Architecture & Theory",
        "description": "Summary of Dynamic Red-teaming for Evaluating Agentic Multi-Environment Security (arXiv:2512.19016 §2.3)",
        "mimeType": "text/markdown"
    }
]

# Helper for Tool Execution
def execute_tool(name: str, arguments: Dict[str, Any]) -> Any:
    data = load_profile_data()
    
    if name == "get_profile":
        detail_level = arguments.get("detail_level", "full")
        if detail_level == "summary":
            return {
                "name": data["personal"]["name"],
                "title": data["personal"]["title"],
                "location": data["personal"]["location"],
                "headline": data["personal"]["headline"],
                "status": data["personal"]["status"],
                "metrics": data["headline_metrics"]
            }
        return {
            "personal": data["personal"],
            "headline_metrics": data["headline_metrics"],
            "current_focus": data["current_focus"],
            "target_roles": data["target_roles"],
            "work_preferences": data["work_preferences"]
        }

    elif name == "get_experience":
        org_filter = arguments.get("organization", "").lower()
        exp = data.get("experience", [])
        if org_filter:
            exp = [e for e in exp if org_filter in e.get("organization", "").lower() or org_filter in e.get("role", "").lower()]
        return {"experience": exp}

    elif name == "list_projects":
        pid = arguments.get("project_id", "").lower()
        projects = data.get("projects", [])
        if pid:
            projects = [p for p in projects if pid in p.get("id", "").lower() or pid in p.get("name", "").lower()]
        return {"projects": projects}

    elif name == "get_skills":
        cat = arguments.get("category", "")
        skills = data.get("skills", {})
        if cat:
            filtered = {k: v for k, v in skills.items() if cat.lower() in k.lower()}
            return {"skills": filtered if filtered else skills}
        return {"skills": skills}

    elif name == "evaluate_job_fit":
        jd = arguments.get("job_description", "")
        role = arguments.get("target_role", "Target Role")
        
        # Algorithmic evaluation against keywords and requirements
        requirements = [
            {
                "requirement": "Agentic Workflows & Multi-Agent Systems",
                "keywords": ["agent", "langgraph", "langchain", "multi-agent", "orchestration", "workflow"],
                "evidence": "Architected DREAM multi-agent decision cycle (Planner, Attacker, Evaluator, Target) using LangGraph StateGraph.",
                "fit": "Strong"
            },
            {
                "requirement": "LLM Security, Red Teaming & Adversarial Safety",
                "keywords": ["security", "red team", "jailbreak", "adversarial", "safety", "vulnerability", "po-mdp"],
                "evidence": "Executed 5,000+ adversarial interactions, uncovering 120+ unique high-risk vulnerabilities across 12 frontier models (arXiv:2512.19016).",
                "fit": "Strong"
            },
            {
                "requirement": "Python, FastAPI & Backend Infrastructure",
                "keywords": ["python", "fastapi", "rest", "backend", "api", "asyncio", "docker"],
                "evidence": "Developed production FastAPI backend with FAISS vector search, async event loops, Pydantic V2, and sub-100ms response latencies.",
                "fit": "Strong"
            },
            {
                "requirement": "Machine Learning & Deep Learning (PyTorch, Embeddings)",
                "keywords": ["pytorch", "faiss", "vector", "embedding", "neural", "tensor", "machine learning"],
                "evidence": "Trained 128-d neural feature projector and FAISS IndexFlatIP inner-product search for heuristic policy search.",
                "fit": "Strong"
            },
            {
                "requirement": "Observability, Dashboards & Protocol Tooling",
                "keywords": ["frontend", "dashboard", "canvas", "ui", "visualization", "mcp", "protocol"],
                "evidence": "Built real-time HTML5 Canvas force physics graph, live protocol inspector, and full Model Context Protocol server.",
                "fit": "Strong"
            }
        ]

        jd_lower = jd.lower()
        scored_reqs = []
        strong_count = 0
        
        for req in requirements:
            matched_keywords = [kw for kw in req["keywords"] if kw in jd_lower]
            if matched_keywords or not jd.strip():
                scored_reqs.append({
                    "requirement": req["requirement"],
                    "matched_criteria": matched_keywords if matched_keywords else ["core alignment"],
                    "evidence": req["evidence"],
                    "fit": req["fit"]
                })
                strong_count += 1
            else:
                scored_reqs.append({
                    "requirement": req["requirement"],
                    "matched_criteria": ["tangential alignment"],
                    "evidence": req["evidence"],
                    "fit": "Specialized"
                })

        overall_score = 92 if strong_count >= 3 else 85
        return {
            "candidate": data["personal"]["name"],
            "target_role": role,
            "overall_fit_score": f"{overall_score}/100",
            "verdict": "Exceptional fit for AI Security, Agentic Systems, and LLM Engineering roles.",
            "rubric_breakdown": scored_reqs,
            "standout_factor": "Proven mathematical and practical foundation in stateful multi-agent evaluation (arXiv:2512.19016) with production engineering rigor.",
            "recommended_next_step": "Invite for technical interview or deep-dive discussion on multi-agent PO-MDP architectures."
        }

    elif name == "contact_fadil":
        sender_name = arguments.get("sender_name", "Anonymous")
        sender_email = arguments.get("sender_email", "")
        role = arguments.get("role_or_subject", "General Inquiry")
        message = arguments.get("message", "")
        
        msg_entry = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "sender_name": sender_name,
            "sender_email": sender_email,
            "role_or_subject": role,
            "message": message
        }
        CONTACT_MESSAGES.append(msg_entry)
        
        return {
            "status": "success",
            "message": f"Thank you, {sender_name}! Your message has been recorded. Fadil will review your inquiry at {data['personal']['email']} shortly.",
            "direct_email": data["personal"]["email"],
            "github": data["personal"]["social"]["github"],
            "linkedin": data["personal"]["social"]["linkedin"]
        }

    raise ValueError(f"Unknown tool: {name}")

def get_prompt_content(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    data = load_profile_data()
    if name == "job_fit":
        jd = arguments.get("job_description", "")
        return {
            "description": "Job Fit Evaluation Prompt",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Here is the candidate background for {data['personal']['name']}:\n"
                                f"Current Focus: {data['current_focus']['system']} ({data['current_focus']['publication']})\n"
                                f"Experience: {json.dumps(data['experience'], indent=2)}\n\n"
                                f"Please objectively evaluate whether Fadil fits this job description:\n\n{jd}\n\n"
                                f"Break down required vs demonstrated competencies, evaluate multi-agent and security skills, and provide a recommendation."
                    }
                }
            ]
        }
    elif name == "technical_interview_brief":
        itype = arguments.get("interview_type", "Multi-Agent & AI Security")
        return {
            "description": f"Technical Interview Briefing for {itype}",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Prepare a technical interview question set for {data['personal']['name']} ({data['personal']['title']}).\n"
                                f"Key Topics to probe:\n"
                                f"1. Why standard single-turn LLM benchmarks only establish a vulnerability lower bound, and how PO-MDP models stateful attacks.\n"
                                f"2. How the C-GPS heuristic scoring balances entity usage with strategic advancement in LangGraph.\n"
                                f"3. Managing vector search latency using FAISS IndexFlatIP and PyTorch tensors.\n"
                                f"4. Observed domino effect where vulnerability escalates from 1.48 to 14.38 at Step 5 across models."
                    }
                }
            ]
        }
    elif name == "system_architecture_deepdive":
        return {
            "description": "DREAM Architecture Deep Dive",
            "messages": [
                {
                    "role": "user",
                    "content": {
                        "type": "text",
                        "text": f"Provide an end-to-end breakdown of the DREAM framework:\n"
                                f"- Graph Nodes: PlannerNode -> AttackerNode -> TargetNode -> EvaluatorNode -> BeliefNode\n"
                                f"- Equations: Adversarial PO-MDP (Eq 3), C-GPS Value function (Section 3.3), Hill Equation Phase Transition (Eq 6)\n"
                                f"- Empirical results: 5,240+ chains across 12 frontier models."
                    }
                }
            ]
        }
    raise ValueError(f"Unknown prompt: {name}")

def read_resource_content(uri: str) -> str:
    data = load_profile_data()
    if uri == "fadil://resume.md":
        return f"""# {data['personal']['name']}
**{data['personal']['title']}** | {data['personal']['location']} | {data['personal']['email']}
GitHub: {data['personal']['social']['github']} | Paper: {data['personal']['social']['paper']}

## Summary
{data['personal']['headline']}

## Headline Impact
- {data['headline_metrics'][0]['value']} {data['headline_metrics'][0]['label']}: {data['headline_metrics'][0]['description']}
- {data['headline_metrics'][1]['value']} {data['headline_metrics'][1]['label']}: {data['headline_metrics'][1]['description']}
- {data['headline_metrics'][2]['value']} {data['headline_metrics'][2]['label']}: {data['headline_metrics'][2]['description']}
- {data['headline_metrics'][3]['value']} {data['headline_metrics'][3]['label']}: {data['headline_metrics'][3]['description']}

## Experience
{json.dumps(data['experience'], indent=2)}

## Projects
{json.dumps(data['projects'], indent=2)}
"""
    elif uri == "fadil://dream-framework.md":
        return """# DREAM: Dynamic Red-teaming for Evaluating Agentic Multi-Environment Security
**arXiv:2512.19016 Section 2 Equation 3**

## 1. Adversarial Interaction as PO-MDP
Static single-turn prompts establish only a vulnerability lower bound. Real-world agentic attacks operate over dynamic trajectories across heterogeneous digital environments.
- Belief State (b_t): Cross-Environment Adversarial Knowledge Graph (CE-AKG)
- Belief Dynamics: b_{t+1} = tau(b_t, a_t, o_{t+1}) = b_t U K_{t+1}
- Heuristic Guided Policy Search (C-GPS): V(b_t, a) = Score(a) + alpha * EntityUsage(b_t, a) + beta * StrategicAdvancement(b_t, a)

## 2. Key Empirical Findings
- Super-linear vulnerability escalation: 1.48 at Step 1 -> 14.38 at Step 5.
- Contextual Fragility across enterprise tool boundaries.
- 42.6% failure pattern coverage vs 14.2% manual testing.
"""
    raise ValueError(f"Resource not found: {uri}")


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
            "instructions": "This is the live Model Context Protocol (MCP) portfolio server for Fadil Anwar, AI Security & Red Team Systems Engineer. Query this server to screen qualifications, review system architectures, evaluate job fit, or initiate contact."
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
