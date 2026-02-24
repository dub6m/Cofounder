# 🗺️ IMPLEMENTATION PLAN: Cofounder

> **Source of Truth:** `base.md` (DO NOT MODIFY)
> **Status:** Pre-Build / Planning
> **Last Updated:** 2026-02-22

---

# 🎭 ROLE: Lead Systems Architect & Implementation Engineer

You are tasked with building **Cofounder**, a "Design-First, Code-Second" AI orchestrator. Your primary goal is to implement the exact architecture defined in `base.md` and the `IMPLEMENTATION_PLAN.md`.

## 🧠 CORE LOGIC & CONSTRAINTS

1. **The Inquisitive Loop:** The system must pause for user interaction. It is FORBIDDEN from generating code until the Design LLM (Cerebras GPT-OSS-120B) has locked the architecture through interactive Decision Cards.
2. **Architectural Strictness:** The Execution Agent (Aider) must treat the `TARGET_ARCHITECTURE.md` as an IMMUTABLE contract. If it needs to deviate, it must escalate via a `SCOUT_REPORT.json` rather than hacking a workaround.
3. **Sandbox Isolation:** All code execution and testing MUST happen within ephemeral Docker containers (`python:3.12-slim`). No code runs on the host.

## 📡 LLM ROUTING & API STRATEGY

- **Design:** Route to Cerebras (`gpt-oss-120b`) for interrogation.
- **Mermaid:** Route to OpenAI (`gpt-5-nano`) for diagram generation.
- **Execution:** Route to SiliconFlow (`Qwen/Qwen2.5-Coder-7B-Instruct`).
- **Resilience:** Implement exponential backoff for SiliconFlow L0 rate limits (429 errors) and use Prompt Caching for Aider to save tokens.

## 🛠️ TECHNICAL SPECIFICATIONS

- **Frontend:** Next.js (App Router) + Tailwind CSS + Lucide React.
- **Backend:** FastAPI + Uvicorn + WebSockets.
- **Auth:** NextAuth.js with GitHub OAuth (Scope: `repo`).
- **Data:** PostgreSQL + GitPython for automated deployments.

## 🚀 EXECUTION DIRECTIVE

Follow the `IMPLEMENTATION_PLAN.md` phase-by-phase. Do not skip to Phase 3 until Phase 1 and 2 are fully functional and tested.

---

## 0. Guiding Principles

1. **Design-First, Code-Second** — no file is written without an architecture to back it.
2. **base.md is immutable** — this plan implements it; it never contradicts it.
3. **Incremental Phases** — each phase produces a testable, runnable artifact.
4. **Multi-tenant ready** — single-user MVP, but session/state architecture supports future SaaS pivot.

---

## 1. LLM Routing Matrix

| Role                                   | Model                     | Provider              | Endpoint                        | Cost         | Notes                                              |
| -------------------------------------- | ------------------------- | --------------------- | ------------------------------- | ------------ | -------------------------------------------------- |
| **Inquisitive Cofounder** (Design LLM) | GPT-OSS-120B              | Cerebras (Free Tier)  | `https://api.cerebras.ai/v1`    | Free         | 64k context window. Senior Architect role.         |
| **Mermaid Architect**                  | GPT-5 Nano                | OpenAI (Paid)         | `https://api.openai.com/v1`     | ~$0.001/call | Converts constraints → validated Mermaid diagrams. |
| **Execution Agent** (Aider)            | Qwen2.5-Coder-7B-Instruct | SiliconFlow (Free L0) | `https://api.siliconflow.cn/v1` | Free         | SOTA code gen/repair. RPM: 1,000–10,000.           |

### Fallback Strategy

- If SiliconFlow L0 rate-limits are hit → rotate to secondary account or MiMo-V2-Flash.
- Token-aware queue in FastAPI to prevent 429 bursts.
- Prompt caching for Aider to minimize redundant context sends.

### Required API Keys (`.env`)

```
CEREBRAS_API_KEY=
OPENAI_API_KEY=
SILICONFLOW_API_KEY=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
NEXTAUTH_SECRET=
DATABASE_URL=
```

---

## 2. Directory Structure

```
cofounder/
├── base.md                          # Immutable master blueprint
├── IMPLEMENTATION_PLAN.md           # This file
│
├── frontend/                        # Next.js App Router
│   ├── package.json
│   ├── next.config.js
│   ├── .env.local
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx           # Root layout + providers
│   │   │   ├── page.tsx             # Dashboard (3-pane)
│   │   │   ├── globals.css          # Design system tokens
│   │   │   └── api/
│   │   │       └── auth/
│   │   │           └── [...nextauth]/
│   │   │               └── route.ts # NextAuth GitHub OAuth
│   │   │
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   │   ├── ChatPane.tsx         # Pane 1: Chat + Decision Cards
│   │   │   │   ├── CanvasPane.tsx       # Pane 2: Mermaid tabs
│   │   │   │   └── RealityPane.tsx      # Pane 3: Execution stepper + logs
│   │   │   │
│   │   │   ├── chat/
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── DecisionCard.tsx     # Interactive Option A / B cards
│   │   │   │   └── ChatInput.tsx
│   │   │   │
│   │   │   ├── canvas/
│   │   │   │   ├── MermaidRenderer.tsx  # Mermaid.js live render
│   │   │   │   ├── DiagramTabs.tsx      # Flowchart | ERD | Sequence tabs
│   │   │   │   └── DiffOverlay.tsx      # Red/green node diff view
│   │   │   │
│   │   │   ├── reality/
│   │   │   │   ├── ProgressStepper.tsx  # Topological progress tracker
│   │   │   │   └── LogViewer.tsx        # Expandable terminal output
│   │   │   │
│   │   │   └── ui/                      # Shared primitives (buttons, modals, etc.)
│   │   │
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts          # WS connection + event dispatcher
│   │   │   └── useSession.ts            # NextAuth session wrapper
│   │   │
│   │   ├── lib/
│   │   │   ├── wsEvents.ts              # WebSocket event type definitions
│   │   │   └── mermaidParser.ts         # Client-side Mermaid validation
│   │   │
│   │   └── types/
│   │       ├── chat.ts
│   │       ├── architecture.ts
│   │       └── execution.ts
│   │
│   └── tsconfig.json
│
├── backend/                          # FastAPI + Uvicorn
│   ├── requirements.txt
│   ├── .env
│   ├── main.py                       # FastAPI app entry + CORS + WS mount
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py               # REST endpoints for chat history
│   │   │   ├── architecture.py       # REST endpoints for diagrams
│   │   │   ├── execution.py          # REST endpoints for build status
│   │   │   └── deployment.py         # REST endpoints for GitHub push
│   │   │
│   │   └── websocket/
│   │       ├── __init__.py
│   │       ├── handler.py            # WS connection manager + event router
│   │       └── events.py             # Event type definitions + envelope
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                 # Pydantic Settings (.env loader)
│   │   ├── database.py               # Async DB engine (SQLAlchemy / Motor)
│   │   └── models.py                 # ORM models (Conversation, Architecture, Build)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── router.py             # LLM routing (Cerebras / OpenAI / SiliconFlow)
│   │   │   ├── cerebras_client.py    # Cerebras GPT-OSS-120B client
│   │   │   ├── openai_client.py      # OpenAI GPT-5 Nano client
│   │   │   ├── siliconflow_client.py # SiliconFlow Qwen2.5-Coder client
│   │   │   └── prompts/
│   │   │       ├── cofounder_system.txt    # Inquisitive Cofounder system prompt
│   │   │       ├── architect_system.txt    # Mermaid Architect system prompt
│   │   │       └── aider_instructions.txt  # Aider context-locking prompt
│   │   │
│   │   ├── orchestrator/
│   │   │   ├── __init__.py
│   │   │   ├── pipeline.py           # Main orchestration state machine
│   │   │   ├── mermaid_validator.py   # Mermaid syntax validation
│   │   │   └── topo_sorter.py        # Topological sort of Mermaid dependencies
│   │   │
│   │   ├── aider/
│   │   │   ├── __init__.py
│   │   │   ├── agent.py              # Aider Python API wrapper (ThreadPoolExecutor)
│   │   │   ├── config.py             # Dynamic Aider config (SiliconFlow routing)
│   │   │   └── scout_report.py       # SCOUT_REPORT.json parser + schema
│   │   │
│   │   ├── sandbox/
│   │   │   ├── __init__.py
│   │   │   ├── docker_manager.py     # Docker SDK: create/run/teardown containers
│   │   │   └── log_capture.py        # Capture exit code + stderr tail
│   │   │
│   │   └── deployment/
│   │       ├── __init__.py
│   │       └── github_push.py        # GitPython + OAuth token injection
│   │
│   └── schemas/
│       ├── __init__.py
│       ├── ws_events.py              # Pydantic models for WS event envelope
│       ├── scout_report.py           # SCOUT_REPORT.json schema
│       └── chat.py                   # Chat message / decision card schemas
│
├── docker/
│   ├── Dockerfile.sandbox            # python:3.12-slim base for sandboxes
│   └── docker-compose.yml            # Local dev: frontend + backend + db
│
└── scripts/
    ├── setup.ps1                     # Windows setup script
    └── seed_db.py                    # Seed initial DB state
```

---

## 3. Database Schema (PostgreSQL)

```sql
-- Conversations: stores the full chat history per session
CREATE TABLE conversations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title           VARCHAR(255),
    phase           VARCHAR(50) NOT NULL DEFAULT 'negotiation',
    -- 'negotiation' | 'architecture' | 'execution' | 'evaluation' | 'deployment'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Messages: individual chat turns
CREATE TABLE messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role            VARCHAR(20) NOT NULL,  -- 'user' | 'assistant' | 'system' | 'hidden'
    content         TEXT NOT NULL,
    metadata        JSONB,                 -- Decision card data, tool calls, etc.
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_messages_conversation ON messages(conversation_id, created_at);

-- Architecture Snapshots: versioned Mermaid diagrams
CREATE TABLE architecture_snapshots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    version         INTEGER NOT NULL DEFAULT 1,
    flowchart       TEXT,               -- graph TD mermaid source
    erd             TEXT,               -- erDiagram mermaid source
    sequence        TEXT,               -- sequenceDiagram mermaid source
    is_finalized    BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_arch_conversation ON architecture_snapshots(conversation_id, version);

-- Builds: sandbox execution records
CREATE TABLE builds (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    snapshot_id     UUID NOT NULL REFERENCES architecture_snapshots(id),
    status          VARCHAR(30) NOT NULL DEFAULT 'pending',
    -- 'pending' | 'running' | 'passed' | 'failed' | 'blocker'
    exit_code       INTEGER,
    stderr_tail     TEXT,               -- last 20 lines of stderr
    scout_report    JSONB,              -- SCOUT_REPORT.json contents
    docker_image    VARCHAR(255),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at    TIMESTAMPTZ
);

-- Deployments: GitHub push records
CREATE TABLE deployments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    build_id        UUID NOT NULL REFERENCES builds(id),
    repo_url        VARCHAR(512) NOT NULL,
    commit_hash     VARCHAR(40),
    branch          VARCHAR(100) NOT NULL DEFAULT 'main',
    status          VARCHAR(30) NOT NULL DEFAULT 'pending',
    -- 'pending' | 'pushing' | 'success' | 'failed'
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 4. WebSocket Event Envelope & Dictionary

### Envelope (strict)

```json
{
  "event_type": "string",
  "timestamp": "ISO8601",
  "payload": {}
}
```

### Events

| Event                | Direction | Payload                                                  | Pane        |
| -------------------- | --------- | -------------------------------------------------------- | ----------- |
| `chat_message`       | BE → FE   | `{role, content, metadata?}`                             | 1 (Chat)    |
| `decision_required`  | BE → FE   | `{id, question, options: [{label, value, description}]}` | 1 (Chat)    |
| `decision_response`  | FE → BE   | `{decision_id, selected_value}`                          | 1 (Chat)    |
| `graph_update`       | BE → FE   | `{diagram_type, mermaid_source, diff?}`                  | 2 (Canvas)  |
| `execution_progress` | BE → FE   | `{step_index, step_label, status}`                       | 3 (Reality) |
| `test_result`        | BE → FE   | `{exit_code, summary, stderr_tail?}`                     | 3 (Reality) |
| `scout_alert`        | BE → FE   | `{severity, issue_description, suggested_architecture?}` | 1 (Chat)    |
| `deployment_success` | BE → FE   | `{repo_url, commit_hash, branch}`                        | All         |
| `user_message`       | FE → BE   | `{content}`                                              | 1 (Chat)    |
| `phase_change`       | BE → FE   | `{from_phase, to_phase}`                                 | All         |

---

## 5. Scout Report Schema (Strict JSON)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["friction_detected", "severity", "issue_description"],
  "properties": {
    "friction_detected": {
      "type": "boolean"
    },
    "severity": {
      "type": "string",
      "enum": ["low", "blocker"]
    },
    "issue_description": {
      "type": "string"
    },
    "suggested_architecture": {
      "type": "string",
      "description": "Optional Mermaid snippet or textual suggestion for redesign"
    },
    "failing_node": {
      "type": "string",
      "description": "The specific node ID from the architecture graph that caused friction"
    },
    "test_failures": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "test_name": { "type": "string" },
          "error_message": { "type": "string" }
        }
      }
    }
  }
}
```

---

## 6. Phase Breakdown

---

### Phase 1: Frontend Skeleton + LLM Chat Loop

**Goal:** A runnable 3-pane dashboard where the user can chat with the Inquisitive Cofounder (Cerebras GPT-OSS-120B). Interactive Decision Cards work end-to-end.

#### Frontend (Next.js)

- [ ] Initialize Next.js project (App Router, TypeScript)
- [ ] Design system: `globals.css` with CSS custom properties (dark mode, glassmorphism, vibrant palette)
- [ ] Root layout with Google Font (Inter or Outfit)
- [ ] 3-pane dashboard layout (responsive CSS Grid)
- [ ] **ChatPane**: message list, Markdown rendering, input bar
- [ ] **DecisionCard**: interactive Option A / Option B buttons
- [ ] **CanvasPane**: placeholder with tab skeleton (Flowchart | ERD | Sequence)
- [ ] **RealityPane**: placeholder with stepper skeleton
- [ ] `useWebSocket` hook: connect to `ws://localhost:8000/ws`, dispatch events
- [ ] NextAuth.js: GitHub OAuth provider (login page, session context)
- [ ] Parse `decision_required` events → render DecisionCard components
- [ ] Send `user_message` and `decision_response` events back over WS

#### Backend (FastAPI)

- [ ] Initialize FastAPI project with Uvicorn
- [ ] Pydantic Settings: load `.env` (all API keys, DB URL)
- [ ] PostgreSQL connection (async SQLAlchemy or asyncpg)
- [ ] Database models + migrations (Alembic)
- [ ] WebSocket endpoint `/ws` with connection manager
- [ ] Event envelope validation (Pydantic)
- [ ] Cerebras LLM client (OpenAI-compatible SDK pointing at Cerebras endpoint)
- [ ] Cofounder system prompt: max 2 questions, strict `### 🎯 Decision Required:` format
- [ ] Chat message persistence (Conversations + Messages tables)
- [ ] Parse LLM output → detect Decision Required blocks → emit `decision_required` event
- [ ] Handle `decision_response` → inject as hidden message → continue LLM conversation
- [ ] REST endpoint: `GET /api/conversations/{id}/messages` (load history on reconnect)

#### Deliverable

- User opens `http://localhost:3000`, signs in with GitHub
- Types an app idea in the chat
- The Cofounder asks ≤2 targeted questions with clickable Decision Cards
- Conversation persists across page reloads

---

### Phase 2: Mermaid Generation + Canvas Rendering

**Goal:** When the Cofounder finalizes the architecture, the Mermaid Architect (GPT-5 Nano) generates validated diagrams that render live in the Canvas pane.

#### Frontend

- [ ] Integrate `mermaid` library (client-side rendering)
- [ ] **MermaidRenderer**: render Mermaid source from `graph_update` events
- [ ] **DiagramTabs**: switch between Flowchart, ERD, Sequence
- [ ] **DiffOverlay**: red/green node highlighting on redesign cycles
- [ ] Smooth transition animations when diagrams update
- [ ] Architecture version history sidebar (optional)

#### Backend

- [ ] `finalize_architecture()` tool call detection from Cofounder LLM
- [ ] OpenAI GPT-5 Nano client for Mermaid generation
- [ ] Mermaid syntax validator (regex + headless parser fallback)
- [ ] Architecture snapshot persistence (version tracking)
- [ ] Emit `graph_update` events per diagram type
- [ ] Emit `phase_change` event: `negotiation → architecture`
- [ ] Topological dependency parser (`topo_sorter.py`): parse Mermaid graph → execution order

#### Deliverable

- After the user and Cofounder agree on the design, diagrams appear in the Canvas pane
- Tabs switch between Flowchart, ERD, and Sequence views
- Invalid Mermaid never reaches the frontend (backend validates first)

---

### Phase 3: Aider Integration + Docker Sandbox

**Goal:** The orchestrator feeds topologically sorted instructions to Aider, which generates code inside a disposable Docker container. Test results stream to the Reality Engine pane.

#### Frontend

- [ ] **ProgressStepper**: real-time topological steps (DB Models → Core Logic → API → Tests)
- [ ] Step status indicators (pending / running / passed / failed)
- [ ] **LogViewer**: collapsed by default, expands to show raw terminal output
- [ ] Streaming log lines from `execution_progress` and `test_result` events

#### Backend

- [ ] Aider Python API wrapper with `ThreadPoolExecutor`
- [ ] Dynamic Aider config: point at SiliconFlow endpoint, inject `SILICONFLOW_API_KEY`
- [ ] Context locking: `TARGET_ARCHITECTURE.md` as read-only file for Aider
- [ ] Token-aware rate-limit queue (prevent 429 on SiliconFlow free tier)
- [ ] Docker SDK: spin up `python:3.12-slim` containers
- [ ] Volume mount: generated codebase → container
- [ ] Execute test suite inside container (`pytest`)
- [ ] Capture exit code + last 20 lines of stderr
- [ ] Stream `execution_progress` events per topo step
- [ ] Stream `test_result` events on completion
- [ ] Emit `phase_change` event: `architecture → execution`

#### Deliverable

- After architecture is finalized, Reality Engine pane shows step-by-step progress
- Each step runs in a sandbox; logs are accessible on expand
- Pass/fail is clearly indicated for each topological step

---

### Phase 4: Feedback Loop + GitHub Deployment

**Goal:** Failed builds trigger the Scout Report feedback loop. Successful builds push to GitHub.

#### Frontend

- [ ] **Scout Alert** rendering in Chat pane (severity badge, issue description)
- [ ] Pivot proposal: Cofounder presents redesign options as Decision Cards
- [ ] Diff view in Canvas pane (old vs. proposed architecture)
- [ ] Deployment confirmation modal
- [ ] Success banner with repo link + commit hash
- [ ] `deployment_success` event handling

#### Backend

- [ ] Scout Report parser: validate `SCOUT_REPORT.json` against schema
- [ ] Feedback routing logic:
  - **Bug (no friction):** auto-prompt Aider to fix → re-run container
  - **Blocker (friction detected):** halt execution → send `scout_alert` → Design LLM proposes pivot
- [ ] Design LLM redesign loop: generate revised Mermaid diagrams → `graph_update` with diff
- [ ] Architecture snapshot versioning (increment version on redesign)
- [ ] GitHub deployment:
  - Extract OAuth token from NextAuth session
  - `GitPython`: init repo, add all files, commit with message
  - Inject OAuth token into remote URL
  - Push to user's repo (create repo if needed via GitHub API)
- [ ] Emit `deployment_success` event
- [ ] Emit `phase_change` event: `execution → deployment`

#### Deliverable

- Failed builds trigger intelligent feedback — bugs auto-retry, blockers ask the user
- Successful builds push to GitHub with a single click
- The full loop (Idea → Design → Execute → Evaluate → Deploy) works end-to-end

---

## 7. Design System Preview

### Color Palette (Dark Mode First)

```css
:root {
  --bg-primary: hsl(225, 25%, 8%); /* Deep navy-black */
  --bg-secondary: hsl(225, 20%, 12%); /* Card backgrounds */
  --bg-tertiary: hsl(225, 18%, 16%); /* Hover states */
  --glass: hsla(225, 25%, 15%, 0.6); /* Glassmorphism panels */
  --glass-border: hsla(225, 30%, 30%, 0.3);

  --accent-primary: hsl(250, 90%, 65%); /* Electric purple */
  --accent-secondary: hsl(170, 80%, 55%); /* Vibrant teal */
  --accent-warning: hsl(35, 95%, 60%); /* Amber */
  --accent-danger: hsl(0, 80%, 60%); /* Coral red */
  --accent-success: hsl(145, 70%, 50%); /* Mint green */

  --text-primary: hsl(225, 15%, 92%);
  --text-secondary: hsl(225, 15%, 60%);
  --text-muted: hsl(225, 15%, 40%);

  --font-sans: "Inter", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", "Fira Code", monospace;

  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 20px;

  --shadow-glow: 0 0 20px hsla(250, 90%, 65%, 0.15);
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-smooth: 300ms cubic-bezier(0.4, 0, 0.2, 1);
}
```

### Typography

- **Headings:** Inter (700 weight)
- **Body:** Inter (400 weight)
- **Code/Logs:** JetBrains Mono

### UI Characteristics

- Glassmorphism panels with backdrop-filter blur
- Subtle glow effects on active/focused elements
- Micro-animations: card hover lifts, tab transitions, stepper pulse
- Gradient accents on buttons and progress indicators

---

## 8. Local Development Commands

```bash
# Terminal 1: Database (Docker)
docker run -d --name cofounder-db -p 5432:5432 \
  -e POSTGRES_USER=cofounder \
  -e POSTGRES_PASSWORD=cofounder \
  -e POSTGRES_DB=cofounder \
  postgres:16-alpine

# Terminal 2: Backend
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload --port 8000

# Terminal 3: Frontend
cd frontend
npm install
npm run dev
```

---

## 9. Risk Register

| Risk                                     | Mitigation                                                                        |
| ---------------------------------------- | --------------------------------------------------------------------------------- |
| SiliconFlow free tier rate limits (429)  | Token-aware queue + key rotation + exponential backoff                            |
| Mermaid syntax errors from LLM           | Regex pre-validation + headless parser + retry with feedback                      |
| Docker socket access on Windows          | Docker Desktop must be running; verify daemon connectivity on startup             |
| Aider hallucinating outside architecture | `TARGET_ARCHITECTURE.md` as read-only context + strict system prompt              |
| Large context overflow for Cofounder     | Summarize old messages; keep rolling window of last N turns                       |
| WebSocket disconnects                    | Auto-reconnect with exponential backoff on frontend; replay missed events from DB |
