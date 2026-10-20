"""
Core portfolio logic for the MCP server: tool/prompt/resource definitions and an
honest, data-driven job-fit evaluator.

Everything user-facing here is derived from data/profile.json. Nothing about the
candidate's experience level, projects or metrics is hardcoded in this module,
except the *mapping* from job-description keywords to the profile evidence that
supports them (see REQUIREMENT_CATALOG), and each mapping states the true level
of that evidence (production vs. project-level vs. listed-only).
"""
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "profile.json"

# In-memory storage for contact messages
CONTACT_MESSAGES: List[Dict[str, Any]] = []


def load_profile_data() -> Dict[str, Any]:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


# ---------------------------------------------------------------------------
# Tool / prompt / resource definitions
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "name": "get_profile",
        "description": "Candidate overview for recruiters and hiring managers: current role, seniority level and years of AI experience, target roles, work preferences, education, headline metrics and links. Start here.",
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
        "description": "Full work history, newest first: organization, role, dates, location, employment type, tech stack and achievements. All roles are internships; seniority is entry-level.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "organization": {
                    "type": "string",
                    "description": "Optional filter by organization or role keyword"
                }
            }
        }
    },
    {
        "name": "list_projects",
        "description": "Projects with descriptions, metrics, tech stack and links (e.g. DREAM red-team service, PharmaGene-RAG, Invoice_AI, AGRIIQ). Includes the status/context of each project.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "Optional project ID or name keyword (e.g. 'dream-redteam', 'pharmagene-rag', 'invoice-ai')"
                }
            }
        }
    },
    {
        "name": "get_skills",
        "description": "Every technical skill mapped to the jobs or projects where it was actually used. A skill that is missing from this list has no evidence; skills marked as listed-only have no project evidence.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional category filter (e.g. 'AI & Agentic Systems', 'Machine Learning & Computer Vision')"
                }
            }
        }
    },
    {
        "name": "evaluate_job_fit",
        "description": "Call when the user shares a job description or asks whether Fadil fits a role. Returns an honest, evidence-based assessment that checks seniority/years of experience first, then maps each requirement to real evidence and flags gaps. Fadil is entry-level (about 6 months of AI internship experience) and only fits associate / graduate / full-time entry-level roles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "job_description": {
                    "type": "string",
                    "description": "The full text of the job description or role requirements"
                },
                "target_role": {
                    "type": "string",
                    "description": "Job title or role being evaluated (e.g. 'Associate AI Engineer')"
                }
            },
            "required": ["job_description"]
        }
    },
    {
        "name": "contact_fadil",
        "description": "Send a direct message to Fadil Anwar. Only call when the user explicitly wants to reach out about an entry-level / associate / graduate opportunity or an intro. Use the user's real email so Fadil can reply.",
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
                    "description": "The message or inquiry"
                }
            },
            "required": ["sender_name", "sender_email", "message"]
        }
    }
]

PROMPTS = [
    {
        "name": "job_fit",
        "description": "Map a job description's requirements to evidence from Fadil's internships and projects, with an honest view of seniority fit.",
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
        "description": "Interviewer briefing: entry-level technical questions drawn from Fadil's real projects (multi-agent red-team harness, RAG, invoice pipeline, computer vision).",
        "arguments": [
            {
                "name": "focus",
                "description": "Optional focus area (e.g. 'agents', 'RAG', 'backend', 'computer vision')",
                "required": False
            }
        ]
    },
    {
        "name": "project_deepdive",
        "description": "Detailed walkthrough request for one of Fadil's projects, using only what is documented in his profile.",
        "arguments": [
            {
                "name": "project_id",
                "description": "Project ID (e.g. 'dream-redteam', 'pharmagene-rag', 'invoice-ai')",
                "required": True
            }
        ]
    }
]

RESOURCES = [
    {
        "uri": "fadil://resume.md",
        "name": "Fadil Anwar - Resume",
        "description": "Markdown resume generated from profile.json: experience, education, awards and headline metrics.",
        "mimeType": "text/markdown"
    },
    {
        "uri": "fadil://projects.md",
        "name": "Fadil Anwar - Projects",
        "description": "All projects with highlights, metrics and tech stacks, generated from profile.json.",
        "mimeType": "text/markdown"
    }
]


# ---------------------------------------------------------------------------
# Seniority helpers
# ---------------------------------------------------------------------------
def get_seniority(data: Dict[str, Any]) -> Dict[str, Any]:
    s = dict(data.get("seniority") or {})
    s.setdefault("level", "Entry-level / Associate")
    s.setdefault("ai_experience_months", 6)
    s.setdefault(
        "ai_experience_summary",
        "About 6 months of applied AI internship experience.",
    )
    return s


def server_instructions() -> str:
    data = load_profile_data()
    personal = data.get("personal", {})
    sen = get_seniority(data)
    return (
        f"Live MCP portfolio server for {personal.get('name')} ({personal.get('title')}). "
        f"Seniority: {sen['level']}. {sen['ai_experience_summary']} "
        "He is looking for associate / graduate / full-time entry-level roles, not lead or senior positions. "
        "Use the tools to inspect experience, projects and skills, run evaluate_job_fit for an honest assessment, "
        "or contact_fadil to reach out. Do not overstate his experience."
    )


# ---------------------------------------------------------------------------
# Job-fit evaluator
# ---------------------------------------------------------------------------
# Each entry maps JD keywords to *what the profile really supports*.
# `level` is the honest strength of the evidence:
#   Strong        - used heavily across several roles/projects
#   Solid         - used in real internship/project work with concrete outcomes
#   Project-level - used in a personal/research project only, not in a team job
#   Foundational  - listed in skills/coursework, no project evidence
#   Limited       - only tangential exposure
LEVEL_WEIGHTS = {
    "Strong": 1.0,
    "Solid": 0.85,
    "Project-level": 0.65,
    "Foundational": 0.35,
    "Limited": 0.2,
}

REQUIREMENT_CATALOG: List[Dict[str, Any]] = [
    {
        "label": "Python",
        "keywords": ["python"],
        "level": "Strong",
        "evidence": "Primary language across all three internships and every project (vision, forecasting, NLP/RAG, agents, backend services).",
    },
    {
        "label": "LLM applications & APIs",
        "keywords": ["llm", "generative ai", "genai", "openai", "gemini", "gpt", "prompt engineering", "large language model"],
        "level": "Solid",
        "evidence": "Integrated LLM components via APIs at Efforts IT Solutions; Invoice_AI uses a confidence-triggered Gemini fallback; DREAM targets GPT-4.",
    },
    {
        "label": "Agentic workflows / multi-agent systems",
        "keywords": ["langgraph", "langchain", "agentic", "multi-agent", "multi agent", "agent framework", "autonomous agent", "agents"],
        "level": "Project-level",
        "evidence": "Built DREAM (planner/attacker/evaluator/target on LangGraph) and a planner/migrator/verifier code-migration agent. Project work, not yet production use in a team setting.",
    },
    {
        "label": "LLM evaluation & adversarial testing",
        "keywords": ["red team", "red-team", "adversarial", "llm evaluation", "evals", "safety evaluation", "jailbreak", "prompt injection", "ai safety"],
        "level": "Project-level",
        "evidence": "DREAM harness triaged 5,000+ automated test executions into 120+ failure categories (~42% failure-taxonomy coverage). Research project (arXiv:2512.19016); no professional AI-safety role.",
    },
    {
        "label": "Security engineering / penetration testing",
        "keywords": ["security engineer", "penetration", "pentest", "appsec", "threat model", "incident response", "vulnerability management", "malware", "soc analyst"],
        "level": "Limited",
        "evidence": "Only CTF participation (malware analysis, AI-based cybersecurity). No professional security engineering experience.",
    },
    {
        "label": "RAG & vector search",
        "keywords": ["rag", "retrieval", "vector database", "vector search", "embedding", "faiss", "chroma", "pinecone", "knowledge graph"],
        "level": "Solid",
        "evidence": "PharmaGene-RAG: hybrid knowledge-graph + vector search with citation enforcement (~60% fewer unsupported clinical claims vs baseline, <3.5s latency). FAISS/Chroma used.",
    },
    {
        "label": "NLP / text classification",
        "keywords": ["nlp", "natural language", "text classification", "transformer", "bert", "roberta"],
        "level": "Solid",
        "evidence": "Built a RoBERTa-based classifier at Emirates (F1 92.3); Kaggle top-20% in an AI-vs-human text-classification competition.",
    },
    {
        "label": "Computer vision",
        "keywords": ["computer vision", "yolo", "object detection", "opencv", "image", "tracking", "geospatial"],
        "level": "Solid",
        "evidence": "AGRIIQ: YOLO11 + ByteTrack + EfficientNet real-time pipeline (~83% lower GPU overhead); drone tree-crown segmentation with DeepForest/Rasterio/PyODM.",
    },
    {
        "label": "Machine learning & forecasting",
        "keywords": ["machine learning", "pytorch", "tensorflow", "lightgbm", "xgboost", "scikit", "forecast", "time-series", "time series", "data science"],
        "level": "Solid",
        "evidence": "PyTorch across vision and agents; LightGBM four-week commodity price forecasts with confidence intervals and 100% prediction coverage via fallback tiers.",
    },
    {
        "label": "Backend services & REST APIs",
        "keywords": ["fastapi", "flask", "rest api", "restful", "backend", "microservice", "api development", "asynchronous", "message queue", "redis", "distributed system"],
        "level": "Solid",
        "evidence": "Invoice_AI: FastAPI + Redis/RQ async workers designed for ~10,000 invoices/day with sub-second ingestion; REST integrations with Zoho CRM, Outlook, Google Calendar, QuickBooks (internship-level).",
    },
    {
        "label": "Databases / SQL",
        "keywords": ["sql", "postgres", "postgresql", "mongodb", "database"],
        "level": "Solid",
        "evidence": "PostgreSQL used in Invoice_AI; SQL and MongoDB listed in skills.",
    },
    {
        "label": "Docker, Linux & CI/CD",
        "keywords": ["docker", "container", "ci/cd", "linux", "devops"],
        "level": "Solid",
        "evidence": "Containerized Python backend services with Docker at Efforts IT Solutions; Linux and CI/CD listed in skills.",
    },
    {
        "label": "Frontend (React / JavaScript)",
        "keywords": ["react", "javascript", "typescript", "frontend", "front-end", "tailwind"],
        "level": "Solid",
        "evidence": "React dashboards in Invoice_AI and the Sales Co-worker platform; HTML5 Canvas graph visualisation.",
    },
    {
        "label": "Cloud (AWS)",
        "keywords": ["aws", "ec2", "lambda", "sqs", "cloudwatch", "cloud", "azure", "gcp"],
        "level": "Foundational",
        "evidence": "AWS services listed (EC2, S3, Lambda, SQS, CloudWatch) with AWS Academy ML Foundations and Cloud Practitioner Foundations coursework. No project in the profile documents hands-on AWS delivery.",
    },
    {
        "label": "Kubernetes / infrastructure-as-code",
        "keywords": ["kubernetes", "k8s", "terraform", "helm", "ansible"],
        "level": "Foundational",
        "evidence": "Kubernetes is listed in skills only; no project evidence. Terraform/Helm/Ansible are not listed at all.",
    },
    {
        "label": "Java / C++",
        "keywords": ["java", "c++"],
        "level": "Foundational",
        "evidence": "Listed as additional languages; no project evidence in the profile.",
    },
]

_SENIOR_TITLE_RE = re.compile(
    r"\b(lead|principal|staff|senior|sr\.?|head of|director|manager|vp)\b", re.IGNORECASE
)
_ENTRY_TITLE_RE = re.compile(
    r"\b(intern|internship|junior|jr\.?|associate|graduate|entry[- ]level|fresher|trainee|early[- ]career)\b",
    re.IGNORECASE,
)
_RANGE_YEARS_RE = re.compile(r"(\d+)\s*(?:-|–|to)\s*(\d+)\s*\+?\s*(?:years?|yrs?)", re.IGNORECASE)
_SINGLE_YEARS_RE = re.compile(r"(\d+)\s*\+?\s*(?:years?|yrs?)", re.IGNORECASE)


def _keyword_found(keyword: str, text: str) -> bool:
    pattern = r"(?<![\w+#])" + re.escape(keyword) + r"(?![\w+#])"
    return re.search(pattern, text, re.IGNORECASE) is not None


def _required_years(jd: str) -> float:
    """Highest minimum-years requirement mentioned in the JD (0 if none)."""
    mins: List[float] = []
    ranged_spans = []
    for m in _RANGE_YEARS_RE.finditer(jd):
        mins.append(float(m.group(1)))
        ranged_spans.append(m.span())
    for m in _SINGLE_YEARS_RE.finditer(jd):
        if any(s <= m.start() < e for s, e in ranged_spans):
            continue
        val = float(m.group(1))
        if val <= 25:
            mins.append(val)
    return max(mins) if mins else 0.0


def evaluate_job_fit(jd: str, role: str, data: Dict[str, Any]) -> Dict[str, Any]:
    seniority = get_seniority(data)
    ai_years = seniority["ai_experience_months"] / 12.0
    name = data.get("personal", {}).get("name", "Candidate")

    title_text = f"{role or ''} {jd.strip()[:200]}"
    senior_title = bool(_SENIOR_TITLE_RE.search(title_text)) and not _ENTRY_TITLE_RE.search(title_text)
    req_years = _required_years(jd)

    # --- 1. Seniority check (always evaluated first) ---------------------
    if senior_title or req_years >= 3:
        level_fit = "Mismatch"
    elif req_years > 1:
        level_fit = "Stretch"
    else:
        level_fit = "Matches"

    detected_level = (
        "Lead / Senior"
        if senior_title
        else ("Associate / Entry-level" if _ENTRY_TITLE_RE.search(title_text) else "Not stated")
    )

    seniority_row = {
        "requirement": "Seniority & years of experience",
        "matched_criteria": [
            f"role level: {detected_level}",
            f"years asked: {int(req_years) if req_years else 'not stated'}",
        ],
        "evidence": (
            f"{seniority['level']}. {seniority['ai_experience_summary']} "
            f"Seeking: {', '.join(seniority.get('seeking', [])) or 'entry-level roles'}."
        ),
        "fit": {"Mismatch": "Gap", "Stretch": "Stretch", "Matches": "Matches"}[level_fit],
    }

    # --- 2. Skill requirements -------------------------------------------
    jd_text = f"{role or ''}\n{jd}"
    rubric: List[Dict[str, Any]] = []
    weights: List[float] = []
    gaps: List[str] = []
    for entry in REQUIREMENT_CATALOG:
        hits = [kw for kw in entry["keywords"] if _keyword_found(kw, jd_text)]
        if not hits:
            continue
        rubric.append({
            "requirement": entry["label"],
            "matched_criteria": hits,
            "evidence": entry["evidence"],
            "fit": entry["level"],
        })
        weights.append(LEVEL_WEIGHTS[entry["level"]])
        if entry["level"] in ("Foundational", "Limited"):
            gaps.append(f"{entry['label']}: {entry['evidence']}")

    skill_score: Optional[float] = (sum(weights) / len(weights) * 100) if weights else None

    # --- 3. Combine into an honest overall score --------------------------
    if level_fit == "Mismatch":
        gaps.insert(
            0,
            f"Seniority: this looks like a {detected_level if detected_level != 'Not stated' else 'senior-level'} role"
            + (f" asking for {int(req_years)}+ years" if req_years else "")
            + f", while the candidate is {seniority['level'].lower()} with about {seniority['ai_experience_months']} months of AI experience.",
        )
        score = min(skill_score if skill_score is not None else 30, 30)
        verdict = (
            "Not a fit at this level. Fadil is entry-level and is looking for associate / graduate / "
            "full-time entry-level roles, not lead or senior positions."
        )
        next_step = (
            "Do not shortlist for this role. If the team has an associate, graduate or junior AI/ML/backend "
            "opening, use contact_fadil to start that conversation."
        )
    elif level_fit == "Stretch":
        score = min(skill_score if skill_score is not None else 50, 60)
        verdict = (
            "Possible stretch. The role asks for 1-2+ years; Fadil has about "
            f"{seniority['ai_experience_months']} months of AI internship experience plus an earlier data-science internship. "
            "Consider only if the team hires early-career engineers."
        )
        next_step = "Review the matched projects below and screen for learning ability and project depth."
    else:
        score = skill_score if skill_score is not None else 50
        if skill_score is None:
            verdict = "Seniority matches an entry-level role, but no recognisable technical requirements were found in the text to score."
        elif score >= 75:
            verdict = "Good fit for an entry-level / associate role, based on documented internships and projects."
        elif score >= 55:
            verdict = "Reasonable fit for an entry-level / associate role; some requirements are project-level or foundational only."
        else:
            verdict = "Partial fit; several requirements have only foundational or limited evidence."
        next_step = "Invite for a technical screen focused on his projects (DREAM, PharmaGene-RAG, Invoice_AI, AGRIIQ)."

    breakdown = [seniority_row] + rubric

    return {
        "candidate": name,
        "target_role": role or "Target Role",
        "seniority_assessment": {
            "candidate_level": seniority["level"],
            "candidate_ai_experience": seniority["ai_experience_summary"],
            "role_level_detected": detected_level,
            "years_required_in_jd": req_years or None,
            "level_fit": level_fit,
        },
        "overall_fit_score": f"{int(round(score))}/100",
        "verdict": verdict,
        "rubric_breakdown": breakdown,
        "gaps": gaps,
        "recommended_next_step": next_step,
        "note": "Scores come from keyword mapping against documented evidence in profile.json; they are a screening aid, not a hiring decision.",
    }


# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------
def execute_tool(name: str, arguments: Dict[str, Any]) -> Any:
    data = load_profile_data()
    personal = data.get("personal", {})

    if name == "get_profile":
        detail_level = arguments.get("detail_level", "full")
        seniority = get_seniority(data)
        if detail_level == "summary":
            return {
                "name": personal.get("name"),
                "title": personal.get("title"),
                "seniority": seniority["level"],
                "ai_experience": seniority["ai_experience_summary"],
                "location": personal.get("location"),
                "headline": personal.get("headline"),
                "status": personal.get("status"),
                "metrics": data.get("headline_metrics", []),
            }
        return {
            "personal": personal,
            "seniority": seniority,
            "about": data.get("about"),
            "headline_metrics": data.get("headline_metrics", []),
            "current_focus": data.get("current_focus"),
            "education": data.get("education", []),
            "awards": data.get("awards", []),
            "target_roles": data.get("target_roles", []),
            "work_preferences": data.get("work_preferences", {}),
        }

    elif name == "get_experience":
        org_filter = (arguments.get("organization") or "").lower()
        exp = data.get("experience", [])
        if org_filter:
            exp = [
                e for e in exp
                if org_filter in e.get("organization", "").lower() or org_filter in e.get("role", "").lower()
            ]
        return {"experience": exp}

    elif name == "list_projects":
        pid = (arguments.get("project_id") or "").lower()
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
        return evaluate_job_fit(
            arguments.get("job_description", ""),
            arguments.get("target_role", ""),
            data,
        )

    elif name == "contact_fadil":
        sender_name = arguments.get("sender_name", "Anonymous")
        sender_email = arguments.get("sender_email", "")
        role = arguments.get("role_or_subject", "General Inquiry")
        message = arguments.get("message", "")

        CONTACT_MESSAGES.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "sender_name": sender_name,
            "sender_email": sender_email,
            "role_or_subject": role,
            "message": message,
        })

        social = personal.get("social", {})
        return {
            "status": "success",
            "message": f"Thank you, {sender_name}! Your message has been recorded. Fadil will review your inquiry shortly.",
            "direct_email": personal.get("email"),
            "github": social.get("github"),
            "linkedin": social.get("linkedin"),
        }

    raise ValueError(f"Unknown tool: {name}")


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
def _project_by_id(data: Dict[str, Any], project_id: str) -> Optional[Dict[str, Any]]:
    pid = (project_id or "").lower()
    for p in data.get("projects", []):
        if pid and (pid in p.get("id", "").lower() or pid in p.get("name", "").lower()):
            return p
    return None


def get_prompt_content(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    data = load_profile_data()
    personal = data.get("personal", {})
    seniority = get_seniority(data)

    if name == "job_fit":
        jd = arguments.get("job_description", "")
        text = (
            f"Candidate: {personal.get('name')} ({seniority['level']}). {seniority['ai_experience_summary']}\n"
            f"Seeking: {', '.join(seniority.get('seeking', []))}. "
            f"Not seeking: {', '.join(seniority.get('not_seeking', []))}.\n\n"
            f"Experience:\n{json.dumps(data.get('experience', []), indent=2)}\n\n"
            f"Projects:\n{json.dumps(data.get('projects', []), indent=2)}\n\n"
            f"Evaluate honestly whether this candidate fits the job description below. Check seniority and "
            f"years of experience FIRST; if the role is lead/senior or asks for 3+ years, say it is not a fit. "
            f"Then map each requirement to documented evidence and clearly label gaps. Do not overstate.\n\n{jd}"
        )
        return {
            "description": "Job Fit Evaluation Prompt",
            "messages": [{"role": "user", "content": {"type": "text", "text": text}}],
        }

    elif name == "technical_interview_brief":
        focus = arguments.get("focus", "")
        project_lines = []
        for p in data.get("projects", []):
            if p.get("metrics") or p.get("id") in ("dream-redteam", "pharmagene-rag", "invoice-ai"):
                project_lines.append(f"- {p['name']}: {p.get('tagline', '')} ({p.get('metrics', 'no metrics listed')})")
        text = (
            f"Prepare an entry-level technical interview question set for {personal.get('name')} "
            f"({seniority['level']}; {seniority['ai_experience_summary']}).\n"
            + (f"Focus area: {focus}\n" if focus else "")
            + "Base the questions strictly on these documented projects:\n"
            + "\n".join(project_lines)
            + "\n\nAsk about design decisions, trade-offs and what he would do differently; do not assume "
              "lead-level experience."
        )
        return {
            "description": "Technical Interview Briefing (entry-level)",
            "messages": [{"role": "user", "content": {"type": "text", "text": text}}],
        }

    elif name == "project_deepdive":
        project = _project_by_id(data, arguments.get("project_id", ""))
        if not project:
            raise ValueError(f"Unknown project: {arguments.get('project_id')}")
        text = (
            f"Give a deep-dive walkthrough of this project using only the information below. "
            f"If something is not documented, say so instead of guessing.\n\n{json.dumps(project, indent=2)}"
        )
        return {
            "description": f"Project deep dive: {project['name']}",
            "messages": [{"role": "user", "content": {"type": "text", "text": text}}],
        }

    raise ValueError(f"Unknown prompt: {name}")


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------
def _projects_markdown(data: Dict[str, Any]) -> str:
    lines = ["# Projects", ""]
    for p in data.get("projects", []):
        lines.append(f"## {p['name']}")
        if p.get("tagline"):
            lines.append(f"_{p['tagline']}_")
        for h in p.get("highlights", []):
            lines.append(f"- {h}")
        if p.get("metrics"):
            lines.append(f"\n**Metrics:** {p['metrics']}")
        if p.get("tech_stack"):
            lines.append(f"**Stack:** {', '.join(p['tech_stack'])}")
        if p.get("github"):
            lines.append(f"**Repo:** {p['github']}")
        lines.append("")
    return "\n".join(lines)


def read_resource_content(uri: str) -> str:
    data = load_profile_data()
    personal = data.get("personal", {})
    social = personal.get("social", {})
    seniority = get_seniority(data)

    if uri == "fadil://resume.md":
        out = [
            f"# {personal.get('name')}",
            f"**{personal.get('title')}** | {seniority['level']} | {personal.get('location')} | {personal.get('email')}",
            f"GitHub: {social.get('github')} | LinkedIn: {social.get('linkedin')}",
            "",
            "## Summary",
            data.get("about") or personal.get("headline", ""),
            "",
            f"**Experience level:** {seniority['ai_experience_summary']}",
            "",
            "## Headline Metrics",
        ]
        for m in data.get("headline_metrics", []):
            out.append(f"- **{m['value']}** {m['label']}: {m['description']}")
        out += ["", "## Experience"]
        for e in data.get("experience", []):
            out.append(f"### {e['role']} - {e['organization']} ({e['period']}, {e.get('location', '')})")
            for a in e.get("achievements", []):
                out.append(f"- {a}")
            out.append("")
        out += ["## Education"]
        for ed in data.get("education", []):
            out.append(f"- {ed['degree']}, {ed['institution']} ({ed['period']})")
        out += ["", "## Awards"]
        for aw in data.get("awards", []):
            out.append(f"- **{aw['name']}**: {aw['description']}")
        out += ["", _projects_markdown(data)]
        return "\n".join(out)

    elif uri == "fadil://projects.md":
        return _projects_markdown(data)

    raise ValueError(f"Resource not found: {uri}")
