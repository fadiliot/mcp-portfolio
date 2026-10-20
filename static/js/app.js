// ==========================================================================
// Fadil Anwar — MCP Portfolio Interactive Engine
// Real-time JSON-RPC 2.0 protocol handler, live console & scenario player
// ==========================================================================

const API_BASE = window.location.origin;
const MCP_ENDPOINT = `${API_BASE}/mcp`;

// Scenario Presets for "Section 01: USE CASES"
// Every claim below is taken from data/profile.json. Fadil is entry-level (about 6 months of AI
// internship experience) and targets associate / graduate / full-time entry-level roles only.
const RECRUITER_JD =
  "Associate AI Engineer (0-2 years). Python, LLM applications and RAG, LangGraph or agent frameworks, " +
  "REST APIs with FastAPI, Docker, SQL. Kubernetes is a plus.";

const SCENARIOS = {
  recruiter: {
    role: "RECRUITER",
    desc: "Screen against an associate-level job description",
    promptBadge: "PROMPT · JOB_FIT",
    promptText: "Associate AI Engineer (0-2 years). Python, LLM applications and RAG, LangGraph or agent frameworks, REST APIs with FastAPI, Docker, SQL. Kubernetes is a plus. Is Fadil Anwar a fit?",
    toolCalls: [
      { tool: "get_profile", params: { detail_level: "summary" }, label: "Seniority, location, headline metrics" },
      { tool: "get_experience", params: {}, label: "Internship history" },
      { tool: "evaluate_job_fit", params: { job_description: RECRUITER_JD, target_role: "Associate AI Engineer" }, label: "Seniority check + requirement mapping" }
    ],
    // Table and verdict are rendered from the live evaluate_job_fit response
    liveEvaluate: { job_description: RECRUITER_JD, target_role: "Associate AI Engineer" }
  },

  hiring_manager: {
    role: "HIRING MANAGER",
    desc: "Check which claims are evidence-backed",
    promptBadge: "PROMPT · AUDIT_CLAIMS",
    promptText: "Audit Fadil's headline claims: 5,000+ test executions, 120+ failure categories, ~83% GPU reduction, 10,000+ invoices/day. What is publicly verifiable and what is self-reported?",
    toolCalls: [
      { tool: "list_projects", params: { project_id: "dream-redteam" }, label: "DREAM red-team harness" },
      { tool: "list_projects", params: { project_id: "invoice-ai" }, label: "Invoice_AI pipeline" },
      { tool: "get_experience", params: {}, label: "Where each result was produced" }
    ],
    table: [
      {
        req: "5,000+ test executions → 120+ failure categories",
        evidence: "DREAM red-team harness. Public GitHub repo and arXiv:2512.19016. A research project, not a production deployment.",
        fit: "Public repo",
        fitClass: "fit-verified"
      },
      {
        req: "~83% lower GPU overhead (AGRIIQ)",
        evidence: "Trajectory subsampling in the YOLO11 + ByteTrack pipeline built during the Dexian India internship. No public repo; self-reported.",
        fit: "Self-reported",
        fitClass: "fit-partial"
      },
      {
        req: "~10,000 invoices/day (Invoice_AI)",
        evidence: "Stated as the supported scale of the Redis/RQ async architecture built during the Efforts IT internship. No public benchmark.",
        fit: "Self-reported",
        fitClass: "fit-partial"
      },
      {
        req: "~70% accuracy gain, ~60% fewer unsupported claims (PharmaGene-RAG)",
        evidence: "Reported versus baseline models in a co-authored, defended research project. No public paper or repo linked in the profile.",
        fit: "Self-reported",
        fitClass: "fit-partial"
      },
      {
        req: "Seniority",
        evidence: "About 6 months of AI internship experience (Efforts IT Solutions, Dexian India) plus an earlier Emirates data-science internship. All roles so far are internships.",
        fit: "Entry-level",
        fitClass: "fit-partial"
      }
    ],
    synthesis: "Strongest evidence is the public DREAM repo and arXiv paper. Industry numbers come from internships and are self-reported, so ask for a walkthrough or references. Treat him as an entry-level / associate candidate."
  },

  founder: {
    role: "FOUNDER / CTO",
    desc: "Find an associate-level builder and reach out",
    promptBadge: "PROMPT · FOUNDER_OUTREACH",
    promptText: "We are an early-stage startup hiring an associate AI engineer. Can Fadil build end-to-end AI features with us, and how do I reach him?",
    toolCalls: [
      { tool: "get_profile", params: { detail_level: "summary" }, label: "Seniority, availability, location" },
      { tool: "list_projects", params: {}, label: "What he has built" },
      { tool: "get_skills", params: { category: "Backend" }, label: "Backend and systems skills with evidence" }
    ],
    table: [
      {
        req: "Ships AI features end-to-end",
        evidence: "Invoice_AI and the Sales Co-worker platform: FastAPI + React + PostgreSQL + Redis, containerized with Docker (internship projects).",
        fit: "Solid",
        fitClass: "fit-verified"
      },
      {
        req: "LLM / RAG product work",
        evidence: "PharmaGene-RAG: hybrid knowledge-graph + vector search with citation enforcement and a local inference pipeline under 3.5s.",
        fit: "Solid",
        fitClass: "fit-verified"
      },
      {
        req: "Computer vision and forecasting",
        evidence: "AGRIIQ real-time vehicle tracking; drone tree-crown segmentation; LightGBM four-week commodity price forecasts with confidence intervals.",
        fit: "Solid",
        fitClass: "fit-verified"
      },
      {
        req: "Owns architecture independently",
        evidence: "All experience so far is internship work. Best as an associate on a team with mentorship rather than as the sole technical owner.",
        fit: "Entry-level",
        fitClass: "fit-partial"
      }
    ],
    synthesis: "A capable associate-level builder across the stack. Expect to onboard and mentor rather than hand over architecture ownership. Use the contact_fadil tool to reach him about full-time associate or graduate roles."
  },

  interviewer: {
    role: "INTERVIEWER",
    desc: "Brief me before the associate-level interview",
    promptBadge: "PROMPT · TECHNICAL_INTERVIEW_BRIEF",
    promptText: "I am interviewing Fadil for an associate AI engineer role. Give me sharp questions based on his real projects.",
    toolCalls: [
      { tool: "list_projects", params: { project_id: "pharmagene-rag" }, label: "RAG grounding project" },
      { tool: "list_projects", params: { project_id: "dream-redteam" }, label: "Multi-agent evaluation project" },
      { tool: "get_skills", params: { category: "AI & Agentic Systems" }, label: "Agent and LLM evaluation skills" }
    ],
    table: [
      {
        req: "DREAM: evaluation harness",
        evidence: "Ask: 'How did you group 5,000+ test executions into 120+ failure categories without human labels, and how would you check the clusters are meaningful?'",
        fit: "Core topic",
        fitClass: "fit-verified"
      },
      {
        req: "PharmaGene-RAG: grounding",
        evidence: "Ask: 'How does citation enforcement reduce unsupported claims, and how did you measure the ~60% reduction against baseline models?'",
        fit: "Core topic",
        fitClass: "fit-verified"
      },
      {
        req: "Invoice_AI: async pipeline",
        evidence: "Ask: 'Why put Redis/RQ workers between ingestion and OCR, and what happens when a job fails or confidence is below 0.85?'",
        fit: "Core topic",
        fitClass: "fit-verified"
      },
      {
        req: "Calibration",
        evidence: "Ask: 'Which parts were your own design and which were guided by a mentor?' All roles so far are internships.",
        fit: "Calibrate",
        fitClass: "fit-partial"
      }
    ],
    synthesis: "Calibrate for an entry-level candidate: probe design decisions, trade-offs and what he would do differently, not large-scale production ownership."
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
      const level = data.seniority && data.seniority.level ? ` · ${data.seniority.level.split(' / ')[0].toUpperCase()}` : '';
      heroTagline.textContent = `${data.personal.name.toUpperCase()} · ${title}${level}`;
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
        seniority: data.seniority ? data.seniority.level : undefined,
        ai_experience: data.seniority ? data.seniority.ai_experience_summary : undefined,
        location: data.personal.location,
        status: data.personal.status
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

  // Render Evidence Matrix Table + synthesis
  const tbody = document.getElementById("scenario-evidence-tbody");
  const noteEl = document.getElementById("scenario-synthesis-note");

  if (data.liveEvaluate) {
    // Table comes straight from the live evaluate_job_fit tool (validated against profile.json)
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="3" style="color: var(--text-dim);">Running evaluate_job_fit on the live server…</td></tr>`;
    }
    if (noteEl) noteEl.textContent = "";
    renderLiveEvaluation(data.liveEvaluate, scenarioKey);
    return;
  }

  if (tbody) {
    tbody.innerHTML = data.table.map(row => `
      <tr>
        <td style="font-weight: 600; color: #fff;">${escapeHtml(row.req)}</td>
        <td style="color: var(--text-muted);">${escapeHtml(row.evidence)}</td>
        <td><span class="fit-tag ${row.fitClass}">${escapeHtml(row.fit)}</span></td>
      </tr>
    `).join("");
  }

  if (noteEl) {
    noteEl.textContent = data.synthesis;
  }
}

// Map the evaluator's honest fit labels to badge styles
function fitClassFor(label) {
  switch (label) {
    case "Strong":
    case "Matches":
      return "fit-strong";
    case "Solid":
      return "fit-verified";
    case "Project-level":
    case "Stretch":
      return "fit-partial";
    default: // Foundational, Limited, Gap
      return "fit-gap";
  }
}

async function renderLiveEvaluation(args, scenarioKey) {
  const tbody = document.getElementById("scenario-evidence-tbody");
  const noteEl = document.getElementById("scenario-synthesis-note");
  try {
    const res = await fetch(MCP_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: Date.now(),
        method: "tools/call",
        params: { name: "evaluate_job_fit", arguments: args }
      })
    });
    const json = await res.json();
    if (scenarioKey !== currentScenario) return; // user switched scenario meanwhile
    const result = JSON.parse(json.result.content[0].text);

    if (tbody) {
      tbody.innerHTML = result.rubric_breakdown.map(row => `
        <tr>
          <td style="font-weight: 600; color: #fff;">${escapeHtml(row.requirement)}</td>
          <td style="color: var(--text-muted);">${escapeHtml(row.evidence)}</td>
          <td><span class="fit-tag ${fitClassFor(row.fit)}">${escapeHtml(row.fit)}</span></td>
        </tr>
      `).join("");
    }
    if (noteEl) {
      noteEl.textContent = `${result.overall_fit_score} · ${result.verdict} ${result.recommended_next_step}`;
    }
  } catch (err) {
    if (tbody) {
      tbody.innerHTML = `<tr><td colspan="3" style="color: var(--text-dim);">Could not reach the MCP server: ${escapeHtml(err.message)}</td></tr>`;
    }
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
