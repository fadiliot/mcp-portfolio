# Fadil Anwar — Live Model Context Protocol (MCP) Portfolio Website

A live **Model Context Protocol (MCP)** server and interactive developer portfolio.

Instead of making recruiters and hiring managers read a static resume, your portfolio operates as an active, queryable AI service that connects to Claude, Cursor, ChatGPT, and custom LLM agents.

---

## ⚡ Key Highlights & Architecture

- **Protocol Compliant:** Fully implements the **Model Context Protocol (MCP) 2024-11-05** specification over HTTP JSON-RPC 2.0 and Server-Sent Events (SSE).
- **Interactive Scenarios (Use Cases):**
  - **Recruiter:** Runs the live `evaluate_job_fit` tool against an associate-level job description. The table is rendered from the server response, not hardcoded.
  - **Hiring Manager:** Separates public, verifiable claims (DREAM repo and arXiv paper) from self-reported internship results.
  - **Founder / CTO:** Shows what an associate-level builder can ship end to end, and what still needs mentorship.
  - **Interviewer:** Entry-level questions drawn from his real projects (DREAM, PharmaGene-RAG, Invoice_AI).
- **Honest job-fit evaluator:** `evaluate_job_fit` checks seniority and years of experience first. Lead/senior roles or 3+ years required are reported as "Not a fit"; each requirement is then mapped to evidence labelled Strong, Solid, Project-level, Foundational or Limited, with gaps listed.
- **Single source of truth:** Experience level, projects, skills and metrics all come from `data/profile.json` (including the `seniority` block).
- **Live Protocol Console:**
  - Real-time JSON-RPC terminal inspector. Run tools (`get_profile`, `get_experience`, `list_projects`, `get_skills`, `evaluate_job_fit`, `contact_fadil`) and inspect request/response frames with millisecond latency metrics.
- **Plug In Your Agent:**
  - 1-click connectors for Claude (Desktop & Code), Cursor, VS Code, ChatGPT, Gemini, and cURL.
- **Cybernetic Glassmorphic UI:**
  - Ultra-fast Vanilla CSS/JS with dark cyber aesthetics, responsive layout, and glowing radar pulse indicators.

---

## 🚀 Quickstart

### 1. Run the Server

From the `mcp-portfolio` directory:

```bash
python start_portfolio.py
```

Or from the repository root:

```bash
python mcp-portfolio/start_portfolio.py
```

The server will automatically detect an available port (defaults to `8000`) and display:

```
=================================================================
 ⚡ FADIL ANWAR — MODEL CONTEXT PROTOCOL (MCP) PORTFOLIO SERVER
=================================================================
 ▶ Web Dashboard & UI:  http://127.0.0.1:8000/
 ▶ Live MCP Endpoint:   http://127.0.0.1:8000/mcp
 ▶ Live SSE Endpoint:   http://127.0.0.1:8000/sse
 ▶ REST Health Check:   http://127.0.0.1:8000/api/health
-----------------------------------------------------------------
 To connect Claude Code CLI:
   claude mcp add --transport http fadil-portfolio http://127.0.0.1:8000/mcp
=================================================================
```

Open **[http://127.0.0.1:8000](http://127.0.0.1:8000)** in your browser to view the interactive website!

---

## 🔌 Connecting to AI Clients

### 1. Claude Desktop
Add the following to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "fadil-portfolio": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-fetch", "http://127.0.0.1:8000/mcp"]
    }
  }
}
```

### 2. Claude Code CLI
Run directly in your terminal:
```bash
claude mcp add --transport http fadil-portfolio http://127.0.0.1:8000/mcp
```

### 3. Cursor & VS Code (.cursor/mcp.json)
```json
{
  "mcpServers": {
    "fadil-portfolio": {
      "url": "http://127.0.0.1:8000/mcp",
      "transport": "http"
    }
  }
}
```

### 4. cURL / Terminal
```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_profile", "arguments": {}}}'
```

---

## 🛠️ Customizing Your Profile Data

All content, metrics, experience, projects, skills, and links can be updated in a single JSON file without touching code:

- [`data/profile.json`](file:///c:/Users/Fadil%20Anwar/Downloads/red%20team/mcp-portfolio/data/profile.json)

Update your social links, add new research papers, or update your availability, and the MCP server + web UI immediately reflect your changes.
