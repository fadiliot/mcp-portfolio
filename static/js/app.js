// ==========================================================================
// Fadil Anwar — MCP Portfolio Interactive Engine
// Real-time JSON-RPC 2.0 protocol handler, live console & scenario player
// ==========================================================================

const API_BASE = window.location.origin;
const MCP_ENDPOINT = `${API_BASE}/mcp`;

// Scenario Presets for "Section 01: USE CASES"
const SCENARIOS = {
  recruiter: {
    role: "RECRUITER",
    desc: "Screen against an AI / Security job description",
    promptBadge: "PROMPT · JOB_FIT",
    promptText: "Candidate screening: Lead AI Security Engineer, 4+ years. Must have deep experience in autonomous agentic workflows (LangGraph), adversarial safety evaluations, and production Python. Is Fadil Anwar a fit?",
    toolCalls: [
      { tool: "get_profile", params: { detail_level: "full" }, label: "Candidate overview, roles, metrics" },
      { tool: "get_experience", params: { organization: "red team" }, label: "Autonomous Red Team & research tenure" },
      { tool: "list_projects", params: { project_id: "dream-redteam" }, label: "DREAM framework & arXiv publication" }
    ],
    table: [
      {
        req: "Multi-Agent & Agentic Workflows",
        evidence: "Architected DREAM multi-agent decision cycle (Planner, Attacker, Evaluator, Target) using LangGraph StateGraph.",
        fit: "Strong",
        fitClass: "fit-strong"
      },
      {
        req: "Adversarial Red Teaming & Safety",
        evidence: "Executed 5,000+ interactions discovering 120+ unique high-risk vulnerabilities across 12 frontier models (arXiv:2512.19016).",
        fit: "Strong",
        fitClass: "fit-strong"
      },
      {
        req: "Production Python & High-Scale Systems",
        evidence: "Engineered FastAPI backend with FAISS vector search, async event loops, Pydantic V2, and sub-100ms response latencies.",
        fit: "Strong",
        fitClass: "fit-strong"
      },
      {
        req: "Deep Learning (PyTorch, Embeddings)",
        evidence: "Implemented 128-d PyTorch neural feature projection & FAISS IndexFlatIP inner-product search for heuristic attack selection.",
        fit: "Specialized",
        fitClass: "fit-verified"
      }
    ],
    synthesis: "Fadil demonstrates deep empirical and architectural alignment. His work directly bridges theoretical PO-MDP policy search with high-performance production agent systems."
  },

  hiring_manager: {
    role: "HIRING MANAGER",
    desc: "Verify production & research claims",
    promptBadge: "PROMPT · AUDIT_CLAIMS",
    promptText: "Audit verified claims: Verify the 5,000+ adversarial interactions, 120+ high-risk vulnerabilities, and mathematical basis of the PO-MDP formulation reported in DREAM (arXiv:2512.19016).",
    toolCalls: [
      { tool: "list_projects", params: { project_id: "dream-redteam" }, label: "Audit DREAM benchmarks & arXiv:2512.19016" },
      { tool: "get_skills", params: { category: "AI & Agentic Systems" }, label: "PO-MDP & C-GPS heuristic implementation" }
    ],
    table: [
      {
        req: "Empirical Attack Volume",
        evidence: "5,240+ multi-step interaction chains evaluated across 12 models (Sonnet 3.5, GPT-4o, Grok-4, Gemini-2.5, Llama-3.1).",
        fit: "Verified",
        fitClass: "fit-verified"
      },
      {
        req: "Vulnerability Escalation Discovery",
        evidence: "Mathematically modeled 'Domino Effect' showing severity increases 4.8x from Step 1 (1.48) to Step 5 (14.38).",
        fit: "Verified",
        fitClass: "fit-verified"
      },
      {
        req: "Failure Mode Coverage",
        evidence: "Uncovered 120+ unique failure modes achieving 42.6% coverage vs 14.2% for manual static testing.",
        fit: "Verified",
        fitClass: "fit-verified"
      }
    ],
    synthesis: "Claims are backed by published mathematical formulations (arXiv:2512.19016 §2.3) and active open-source implementation with 10/10 automated tests passing."
  },

  founder: {
    role: "FOUNDER / CTO",
    desc: "Find an agentic builder and reach out",
    promptBadge: "PROMPT · FOUNDER_OUTREACH",
    promptText: "We need an engineer who can independently own agent architecture, move fast, and build mission-critical autonomous systems. What can Fadil build?",
    toolCalls: [
      { tool: "get_profile", params: { detail_level: "summary" }, label: "Candidate capabilities & availability" },
      { tool: "get_experience", params: {}, label: "Full stack engineering & autonomy" }
    ],
    table: [
      {
        req: "End-to-End Ownership",
        evidence: "Architected complete multi-agent orchestrator, vector search engine, FastAPI REST API, and HTML5 Canvas physics UI.",
        fit: "Strong",
        fitClass: "fit-strong"
      },
      {
        req: "High-Velocity Prototyping",
        evidence: "Built production-grade, stateful AI security framework from research paper formulation to live testbed.",
        fit: "Strong",
        fitClass: "fit-strong"
      },
      {
        req: "Founding Engineer Mindset",
        evidence: "Comfortable navigating ambiguous agentic frontiers, designing clean protocols (MCP, REST), and optimizing sub-100ms systems.",
        fit: "Strong",
        fitClass: "fit-strong"
      }
    ],
    synthesis: "Fadil operates as a full-stack AI builder who seamlessly connects low-level neural tensors and graph dynamics with high-level user interfaces and APIs."
  },

  interviewer: {
    role: "INTERVIEWER",
    desc: "Brief me before the technical interview",
    promptBadge: "PROMPT · TECHNICAL_INTERVIEW_BRIEF",
    promptText: "I am interviewing Fadil for a Senior AI / Security Engineer role in 15 minutes. Give me the sharpest technical questions based on his real systems.",
    toolCalls: [
      { tool: "list_projects", params: { project_id: "dream-redteam" }, label: "Architecture & algorithmic specifics" },
      { tool: "get_skills", params: { category: "Deep Learning & Search" }, label: "PyTorch & FAISS performance design" }
    ],
    table: [
      {
        req: "Topic 1: Static vs Dynamic Safety",
        evidence: "Ask: 'Why do single-turn jailbreak benchmarks fail to capture multi-agent vulnerabilities, and how does PO-MDP belief tracking solve this?'",
        fit: "Core Topic",
        fitClass: "fit-verified"
      },
      {
        req: "Topic 2: C-GPS Value Heuristic",
        evidence: "Ask: 'How does your heuristic value function balance entity usage with strategic progression when traversing the Atom Attack Library?'",
        fit: "Core Topic",
        fitClass: "fit-verified"
      },
      {
        req: "Topic 3: Real-Time Vector Search",
        evidence: "Ask: 'How did you tune FAISS IndexFlatIP inner-product search and PyTorch embeddings to maintain sub-100ms cycle times?'",
        fit: "Core Topic",
        fitClass: "fit-verified"
      }
    ],
    synthesis: "Focus the conversation on how he prevents infinite loops in cyclic LangGraph workflows and the practical challenges of evaluating non-deterministic LLMs."
  }
};

// Client Connection Snippets
function getClientSnippets(mcpUrl) {
  const isLocal = mcpUrl.includes("localhost") || mcpUrl.includes("127.0.0.1");
  const cloudNote = isLocal 
    ? "\n\n💡 Note for Cloud AIs (ChatGPT / Claude Web): Cloud servers cannot reach localhost. Run 'ngrok http 8000' or deploy to Render/Railway for an HTTPS URL." 
    : "";

  return {
    claude: {
      steps: [
        "Open Claude Desktop or Claude Code CLI",
        "Add connector via stdio (Desktop) or HTTP (Claude Code)",
        "Query Fadil's background directly in your chat"
      ],
      label: "Claude Desktop Config (Local stdio - ~/Library/Application Support/Claude/claude_desktop_config.json or %APPDATA%\\Claude)",
      code: JSON.stringify({
        mcpServers: {
          "fadil-portfolio": {
            "command": "python",
            "args": [
              "c:\\Users\\Fadil Anwar\\Downloads\\red team\\mcp-portfolio\\server\\mcp_stdio.py"
            ]
          }
        }
      }, null, 2),
      altLabel: "Claude Code CLI Command (Local / Remote HTTP)",
      altCode: `claude mcp add --transport http fadil-portfolio ${mcpUrl}`,
      prompt: "What are Fadil's key engineering systems and achievements?"
    },

    cursor: {
      steps: [
        "Open Cursor Settings → Features → MCP",
        "Click '+ Add New MCP Server'",
        "Paste the server definition below into .cursor/mcp.json"
      ],
      label: "Cursor / VS Code MCP Configuration (.cursor/mcp.json)",
      code: JSON.stringify({
        mcpServers: {
          "fadil-portfolio": {
            "url": mcpUrl,
            "transport": "http"
          }
        }
      }, null, 2),
      altLabel: "Terminal Test",
      altCode: `curl -X POST ${mcpUrl} -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'`,
      prompt: "Examine Fadil's get_experience and evaluate his background for an AI Engineer role."
    },

    chatgpt: {
      steps: [
        "Create a Custom GPT or ChatGPT Action",
        "Set Authentication to 'None'",
        "Provide public endpoint URL (or run 'ngrok http 8000' for local testing)"
      ],
      label: "ChatGPT Action Server URL",
      code: `${API_BASE}/api/tools${cloudNote}`,
      altLabel: "Direct REST Profile Endpoint",
      altCode: `${API_BASE}/api/profile`,
      prompt: "Evaluate candidate Fadil Anwar using his projects and experience."
    },

    gemini: {
      steps: [
        "Open Google AI Studio or Vertex AI Workbench",
        "Define Function Calling tool pointing to the MCP tools schema",
        "Connect system instructions to live profile query"
      ],
      label: "Gemini Function Calling Endpoint",
      code: `${API_BASE}/mcp${cloudNote}`,
      altLabel: "Curl Schema Fetch",
      altCode: `curl -s ${API_BASE}/api/tools | jq .`,
      prompt: "Summarize the technical background and key projects of Fadil Anwar."
    },

    grok: {
      steps: [
        "Open Grok API or Agent environment",
        "Include MCP JSON-RPC tool definitions in tool call loop",
        "Query live portfolio tools"
      ],
      label: "MCP JSON-RPC 2.0 URL",
      code: `${mcpUrl}${cloudNote}`,
      altLabel: "Handshake Request",
      altCode: `{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}`,
      prompt: "Ask about Fadil's projects and engineering experience."
    },

    curl: {
      steps: [
        "Open your local terminal or bash shell",
        "Run standard JSON-RPC 2.0 curl command",
        "Inspect instant JSON response"
      ],
      label: "cURL Tool Execution (get_profile)",
      code: `curl -X POST ${mcpUrl} \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_profile", "arguments": {}}}'`,
      altLabel: "List Available Tools",
      altCode: `curl -X POST ${mcpUrl} \\
  -H "Content-Type: application/json" \\
  -d '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}'`,
      prompt: "Query raw protocol directly via curl or Python requests."
    }
  };
}

// Global protocol log cache
let protocolLogLines = [];

// ==========================================================================
// Initialization & Latency Ping
// ==========================================================================
document.addEventListener("DOMContentLoaded", async () => {
  initEndpointUrls();
  measureLatency();
  await loadDynamicProfile();
  initScenarioPlayer("recruiter");
  initLiveConsoleBootSequence();
  initConnectTabs();
  initContactForm();

  // Periodic latency measurement
  setInterval(measureLatency, 15000);
});

// Dynamic Profile Hydration from /api/profile
async function loadDynamicProfile() {
  try {
    const res = await fetch(`${API_BASE}/api/profile`, { cache: "no-store" });
    if (!res.ok) return;
    const data = await res.json();
    if (!data || !data.personal) return;

    // 1. Browser Tab Title & Meta
    document.title = `${data.personal.name} | ${data.personal.title || 'Portfolio'} (MCP Server)`;

    // 2. Navbar Brand
    const brandLink = document.getElementById("brand-link");
    if (brandLink) {
      const firstName = (data.personal.name || 'FADIL').split(' ')[0].toUpperCase();
      brandLink.innerHTML = `<span class="brand-icon">⚡</span> <span>${escapeHtml(firstName)}</span> <span class="brand-tag">/mcp</span>`;
    }

    // 3. Hero Section (Tagline & Description)
    const heroTagline = document.getElementById("hero-tagline");
    if (heroTagline) {
      const title = data.personal.title ? data.personal.title.toUpperCase() : 'APPLIED AI ENGINEER';
      heroTagline.textContent = `${data.personal.name.toUpperCase()} · ${title}`;
    }

    const heroDesc = document.getElementById("hero-description");
    if (heroDesc && data.personal.headline) {
      heroDesc.textContent = data.personal.headline;
    }

    // 4. Hero Live JSON Preview Card
    const heroJsonCode = document.querySelector(".hero-json-preview code");
    if (heroJsonCode) {
      const previewObj = {
        name: data.personal.name,
        role: data.personal.title,
        location: data.personal.location,
        status: data.personal.status,
        headline_metrics: (data.headline_metrics || []).slice(0, 3).map(m => `${m.value} ${m.label}`),
        current_focus: data.current_focus ? (data.current_focus.role || data.current_focus.system) : undefined
      };
      heroJsonCode.innerHTML = renderHighlightedJson(previewObj);
    }

    // 5. Scenario topbar connection label
    const agentStatusLabel = document.querySelector(".agent-connect-status");
    if (agentStatusLabel) {
      const handle = data.personal.handle || data.personal.name.toLowerCase().split(' ')[0];
      agentStatusLabel.innerHTML = `<span class="status-dot"></span> <span>YOUR AGENT · CONNECTED TO <strong>${escapeHtml(handle)}</strong></span>`;
    }

    // 6. Section 04: Profile & Impact Overview Card
    const aboutCard = document.querySelector(".about-card");
    if (aboutCard) {
      const nameHeader = aboutCard.querySelector("h3");
      if (nameHeader) nameHeader.textContent = data.personal.name;

      const bioP = aboutCard.querySelector("p");
      if (bioP && data.personal.headline) bioP.textContent = data.personal.headline;

      // Render all headline metrics dynamically
      const metricsGrid = aboutCard.querySelector(".metrics-highlight-grid");
      if (metricsGrid && data.headline_metrics && data.headline_metrics.length > 0) {
        metricsGrid.innerHTML = data.headline_metrics.map(m => `
          <div class="metric-box">
            <div class="metric-val">${escapeHtml(m.value)}</div>
            <div class="metric-lbl"><strong>${escapeHtml(m.label)}</strong>: ${escapeHtml(m.description || '')}</div>
          </div>
        `).join("");
      }

      // Render social / contact pills
      const linksContainer = aboutCard.querySelector("div[style*='display: flex']");
      if (linksContainer) {
        const social = data.personal.social || {};
        let linksHtml = "";
        if (social.github) {
          linksHtml += `<a href="${escapeHtml(social.github)}" target="_blank" class="btn-copy" style="text-decoration: none;">GitHub: @${escapeHtml(data.personal.handle || 'fadiliot')}</a> `;
        }
        if (social.paper) {
          linksHtml += `<a href="${escapeHtml(social.paper)}" target="_blank" class="btn-copy" style="text-decoration: none;">Research / Paper</a> `;
        }
        if (data.personal.email) {
          linksHtml += `<a href="mailto:${escapeHtml(data.personal.email)}" class="btn-copy" style="text-decoration: none;">${escapeHtml(data.personal.email)}</a> `;
        }
        if (data.personal.phone) {
          linksHtml += `<a href="tel:${escapeHtml(data.personal.phone)}" class="btn-copy" style="text-decoration: none;">${escapeHtml(data.personal.phone)}</a> `;
        }
        linksContainer.innerHTML = linksHtml;
      }
    }

  } catch (err) {
    console.warn("Could not dynamically load profile.json:", err);
  }
}

function renderHighlightedJson(obj) {
  const jsonStr = JSON.stringify(obj, null, 2);
  return jsonStr.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
    let cls = 'json-val';
    if (/^"/.test(match)) {
      if (/:$/.test(match)) {
        cls = 'json-key';
      } else {
        cls = 'json-str';
      }
    }
    return `<span class="${cls}">${escapeHtml(match)}</span>`;
  });
}

// Update displayed endpoint URLs
function initEndpointUrls() {
  const urlBoxes = document.querySelectorAll(".endpoint-url-text");
  urlBoxes.forEach(el => {
    el.textContent = MCP_ENDPOINT;
  });
}

// Measure roundtrip latency to the server
async function measureLatency() {
  const start = performance.now();
  try {
    const res = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
    const duration = Math.round(performance.now() - start);
    if (res.ok) {
      document.querySelectorAll(".live-latency-val").forEach(el => {
        el.textContent = `${duration}ms`;
      });
      document.querySelectorAll(".status-badge-text").forEach(el => {
        el.textContent = `ONLINE ${duration}MS`;
      });
    }
  } catch (err) {
    document.querySelectorAll(".status-badge-text").forEach(el => {
      el.textContent = "STANDBY";
    });
  }
}

// ==========================================================================
// Section 01: USE CASES Engine
// ==========================================================================
let currentScenario = "recruiter";

function initScenarioPlayer(scenarioKey) {
  currentScenario = scenarioKey;
  const data = SCENARIOS[scenarioKey];
  if (!data) return;

  // Highlight active button
  document.querySelectorAll(".scenario-btn").forEach(btn => {
    btn.classList.toggle("active", btn.dataset.scenario === scenarioKey);
  });

  // Update prompt box
  const badgeEl = document.getElementById("scenario-prompt-badge");
  const textEl = document.getElementById("scenario-prompt-text");
  if (badgeEl) badgeEl.textContent = data.promptBadge;
  if (textEl) textEl.textContent = data.promptText;

  // Render Tool Calls
  const toolContainer = document.getElementById("scenario-tool-calls");
  if (toolContainer) {
    toolContainer.innerHTML = "";
    data.toolCalls.forEach((tc, idx) => {
      const item = document.createElement("div");
      item.className = "tool-call-item";
      item.id = `tool-call-${idx}`;
      item.innerHTML = `
        <div class="tool-call-header" onclick="toggleToolCallAccordion(${idx})">
          <div class="tool-call-name">
            <span>› tools/call</span>
            <strong style="color: var(--accent-green);">${tc.tool}</strong>
          </div>
          <div class="tool-call-meta">
            <span id="tc-badge-${idx}">✓ 24ms · 4.8 KB</span>
            <span style="font-size: 0.7rem; color: var(--text-dim);">▼</span>
          </div>
        </div>
        <div class="tool-call-body" id="tc-body-${idx}">
          Loading payload from live MCP server...
        </div>
      `;
      toolContainer.appendChild(item);

      // Fetch real payload from server for this tool
      fetchToolCallForScenario(tc.tool, tc.params, idx);
    });
  }

  // Render Evidence Matrix Table
  const tbody = document.getElementById("scenario-evidence-tbody");
  if (tbody) {
    tbody.innerHTML = data.table.map(row => `
      <tr>
        <td style="font-weight: 600; color: #fff;">${escapeHtml(row.req)}</td>
        <td style="color: var(--text-muted);">${escapeHtml(row.evidence)}</td>
        <td><span class="fit-tag ${row.fitClass}">${escapeHtml(row.fit)}</span></td>
      </tr>
    `).join("");
  }

  // Render Agent Synthesis Note
  const noteEl = document.getElementById("scenario-synthesis-note");
  if (noteEl) {
    noteEl.textContent = data.synthesis;
  }
}

// Fetch live response for scenario accordion
async function fetchToolCallForScenario(toolName, params, index) {
  const start = performance.now();
  try {
    const res = await fetch(MCP_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: index + 10,
        method: "tools/call",
        params: { name: toolName, arguments: params }
      })
    });
    const duration = Math.round(performance.now() - start);
    const json = await res.json();
    const bodyEl = document.getElementById(`tc-body-${index}`);
    const badgeEl = document.getElementById(`tc-badge-${index}`);

    let textContent = "";
    if (json.result && json.result.content && json.result.content[0]) {
      textContent = json.result.content[0].text;
    } else {
      textContent = JSON.stringify(json, null, 2);
    }

    const sizeKb = (new Blob([textContent]).size / 1024).toFixed(1);
    if (badgeEl) badgeEl.textContent = `✓ ${duration}ms · ${sizeKb} KB`;
    if (bodyEl) bodyEl.textContent = textContent;
  } catch (err) {
    const bodyEl = document.getElementById(`tc-body-${index}`);
    if (bodyEl) bodyEl.textContent = `Error fetching tool response: ${err.message}`;
  }
}

function toggleToolCallAccordion(index) {
  const item = document.getElementById(`tool-call-${index}`);
  if (item) {
    item.classList.toggle("open");
  }
}

function replayCurrentScenario() {
  const animEl = document.getElementById("scenario-workspace");
  if (animEl) {
    animEl.style.opacity = "0.4";
    setTimeout(() => {
      initScenarioPlayer(currentScenario);
      animEl.style.opacity = "1";
    }, 200);
  }
}

// ==========================================================================
// Section 02: LIVE CONSOLE (Watch the Protocol)
// ==========================================================================
function initLiveConsoleBootSequence() {
  const termEl = document.getElementById("terminal-scroll-area");
  if (!termEl) return;

  termEl.innerHTML = "";
  appendProtocolLine("out", `POST ${MCP_ENDPOINT} (fadil-anwar-portfolio-mcp)`);
  appendProtocolLine("in", "initialize", "protocol 2024-11-05 · v1.0.0", "18ms");
  appendProtocolLine("in", "notifications/initialized", "202 Accepted", "14ms");
  appendProtocolLine("in", "tools/list", "6 tools · 3 prompts · 2 resources ready", "22ms");
}

function appendProtocolLine(direction, mainText, meta = "", time = "") {
  const termEl = document.getElementById("terminal-scroll-area");
  if (!termEl) return;

  const line = document.createElement("div");
  line.className = "protocol-line";
  
  const isOut = direction === "out";
  line.innerHTML = `
    <span class="${isOut ? 'line-arrow-out' : 'line-arrow-in'}">${isOut ? '→' : '←'}</span>
    <span class="line-content">${escapeHtml(mainText)}</span>
    ${meta ? `<span class="line-meta">${escapeHtml(meta)}</span>` : ""}
    ${time ? `<span class="line-meta" style="color: var(--accent-green);">${escapeHtml(time)}</span>` : ""}
  `;
  termEl.appendChild(line);
  termEl.scrollTop = termEl.scrollHeight;

  protocolLogLines.push(`[${new Date().toISOString()}] ${isOut ? '→' : '←'} ${mainText} ${meta} ${time}`);
}

function appendProtocolJson(data) {
  const termEl = document.getElementById("terminal-scroll-area");
  if (!termEl) return;

  const jsonBlock = document.createElement("div");
  jsonBlock.className = "line-json-block";
  jsonBlock.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
  termEl.appendChild(jsonBlock);
  termEl.scrollTop = termEl.scrollHeight;
}

// Execute live tool when clicking [▷ RUN]
async function runConsoleTool(toolName, customArgs = {}) {
  appendProtocolLine("out", `tools/call ${toolName}`, JSON.stringify(customArgs));

  const start = performance.now();
  try {
    const res = await fetch(MCP_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: Date.now(),
        method: "tools/call",
        params: {
          name: toolName,
          arguments: customArgs
        }
      })
    });

    const duration = Math.round(performance.now() - start);
    const json = await res.json();

    if (json.error) {
      appendProtocolLine("in", `Error (${json.error.code}): ${json.error.message}`, "", `${duration}ms`);
      return;
    }

    let resultText = "";
    if (json.result && json.result.content && json.result.content[0]) {
      resultText = json.result.content[0].text;
    } else {
      resultText = JSON.stringify(json.result, null, 2);
    }

    const sizeKb = (new Blob([resultText]).size / 1024).toFixed(1);
    appendProtocolLine("in", `${toolName} response`, `${sizeKb} KB`, `${duration}ms`);
    appendProtocolJson(resultText);

    showToast(`Ran ${toolName} successfully (${duration}ms)`);
  } catch (err) {
    appendProtocolLine("in", `Network Error: ${err.message}`, "failed");
  }
}

// Execute prompt template
async function runConsolePrompt(promptName, customArgs = {}) {
  appendProtocolLine("out", `prompts/get ${promptName}`, JSON.stringify(customArgs));
  const start = performance.now();
  try {
    const res = await fetch(MCP_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: Date.now(),
        method: "prompts/get",
        params: {
          name: promptName,
          arguments: customArgs
        }
      })
    });
    const duration = Math.round(performance.now() - start);
    const json = await res.json();
    appendProtocolLine("in", `Prompt ${promptName} rendered`, "", `${duration}ms`);
    appendProtocolJson(json.result);
  } catch (err) {
    appendProtocolLine("in", `Error: ${err.message}`);
  }
}

function clearConsoleLog() {
  const termEl = document.getElementById("terminal-scroll-area");
  if (termEl) termEl.innerHTML = "";
  protocolLogLines = [];
  initLiveConsoleBootSequence();
  showToast("Console traffic cleared");
}

function copyConsoleLog() {
  const text = protocolLogLines.join("\n");
  navigator.clipboard.writeText(text);
  showToast("Protocol log copied to clipboard");
}

// ==========================================================================
// Section 03: CONNECT Tabs
// ==========================================================================
function initConnectTabs() {
  const snippets = getClientSnippets(MCP_ENDPOINT);
  const tabBtns = document.querySelectorAll(".client-tab-btn");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      const client = btn.dataset.client;
      tabBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      renderConnectClient(client, snippets);
    });
  });

  // Default to Claude
  renderConnectClient("claude", snippets);
}

function renderConnectClient(clientKey, snippets) {
  const data = snippets[clientKey] || snippets.claude;
  
  // Render Steps
  const stepsContainer = document.getElementById("connect-steps-container");
  if (stepsContainer) {
    stepsContainer.innerHTML = data.steps.map((s, idx) => `
      <div class="step-item">
        <span class="step-num">${idx + 1}</span>
        <span>${escapeHtml(s)}</span>
      </div>
    `).join("");
  }

  // Render Snippet 1
  const label1 = document.getElementById("snippet-1-label");
  const code1 = document.getElementById("snippet-1-code");
  if (label1) label1.textContent = data.label;
  if (code1) code1.textContent = data.code;

  // Render Snippet 2
  const label2 = document.getElementById("snippet-2-label");
  const code2 = document.getElementById("snippet-2-code");
  if (label2) label2.textContent = data.altLabel;
  if (code2) code2.textContent = data.altCode;

  // Render Suggested Prompt
  const promptEl = document.getElementById("connect-suggested-prompt");
  if (promptEl) {
    promptEl.innerHTML = `Then ask: <strong>"${escapeHtml(data.prompt)}"</strong>`;
  }
}

// ==========================================================================
// Section 04: Contact Form Submission
// ==========================================================================
function initContactForm() {
  const form = document.getElementById("direct-contact-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = form.querySelector("button[type='submit']");
    btn.disabled = true;
    btn.textContent = "Sending message...";

    const payload = {
      name: document.getElementById("contact-name").value,
      email: document.getElementById("contact-email").value,
      subject: document.getElementById("contact-subject").value || "Portfolio Outreach",
      message: document.getElementById("contact-message").value
    };

    try {
      const res = await fetch(`${API_BASE}/api/contact`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (res.ok) {
        showToast(data.message || "Message sent successfully!");
        form.reset();
      } else {
        showToast("Error sending message. Please try email.");
      }
    } catch (err) {
      showToast("Network error. Please email directly.");
    } finally {
      btn.disabled = false;
      btn.textContent = "Send Message →";
    }
  });
}

// ==========================================================================
// Utilities: Copy to Clipboard & Toast
// ==========================================================================
function copyToClipboard(text, customMessage = "Copied to clipboard!") {
  if (!text) return;
  navigator.clipboard.writeText(text).then(() => {
    showToast(customMessage);
  }).catch(() => {
    // Fallback
    const input = document.createElement("input");
    input.value = text;
    document.body.appendChild(input);
    input.select();
    document.execCommand("copy");
    document.body.removeChild(input);
    showToast(customMessage);
  });
}

function copyEndpointUrl() {
  copyToClipboard(MCP_ENDPOINT, "MCP endpoint URL copied!");
}

function copySnippet(elementId) {
  const el = document.getElementById(elementId);
  if (el) {
    copyToClipboard(el.textContent.trim(), "Snippet copied to clipboard!");
  }
}

let toastTimeout;
function showToast(message) {
  let toast = document.getElementById("app-toast");
  if (!toast) {
    toast = document.createElement("div");
    toast.id = "app-toast";
    toast.className = "toast";
    document.body.appendChild(toast);
  }

  toast.innerHTML = `
    <span style="color: var(--accent-green); font-weight: bold;">●</span>
    <span>${escapeHtml(message)}</span>
  `;
  toast.classList.add("show");

  clearTimeout(toastTimeout);
  toastTimeout = setTimeout(() => {
    toast.classList.remove("show");
  }, 3200);
}

function escapeHtml(str) {
  if (typeof str !== "string") return str;
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
