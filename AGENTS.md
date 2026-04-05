# AGENTS.md

## 1. Purpose & Audience

This is the canonical coordination document for **all contributors** to this repository — AI coding agents (Claude Code, GitHub Copilot, Cursor, etc.) and humans alike. Every contributor must follow the workflow defined here so that any agent or person can pick up work without hidden chat memory or tool-specific context.

Tool-specific instructions (e.g., `CLAUDE.md`, `.github/agents/`) extend this document but never override it.

---

## 2. Project Overview

**Aviation Ops Briefing Agent** — An LLM-powered aviation operations briefing system that generates contextual operational briefings by combining weather data, NOTAMs, airport information, and operational rules.

### Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.12 |
| Agent framework | LangGraph ≥0.2, LangChain ≥0.3 |
| LLM providers | OpenAI (primary), HuggingFace (alternative) |
| Observability | LangSmith |
| API | FastAPI ≥0.115, Uvicorn |
| Database | PostgreSQL 16 + pgvector (async via SQLAlchemy ≥2.0 + asyncpg) |
| Validation | Pydantic ≥2.0, pydantic-settings |
| Templating | Jinja2 |
| HTTP client | httpx |
| Logging | structlog |
| Rate limiting | slowapi |
| Package manager | uv (with hatchling build backend) |
| Linting/formatting | Ruff (line-length=100, rules: E, F, I) |
| Testing | pytest + pytest-asyncio (asyncio_mode=auto) |
| Containerization | Docker (python:3.12-slim), Docker Compose |

---

## 3. Repository Map

```
├── AGENTS.md                    # ← You are here. Global coordination rules.
├── CLAUDE.md                    # Claude-specific instructions (extends AGENTS.md)
├── pyproject.toml               # Dependencies, build config, tool settings
├── docker-compose.yml           # App + PostgreSQL/pgvector services
├── Dockerfile                   # Production image (uv, non-root user)
├── .env.example                 # Required environment variables template
│
├── src/                         # Application source code
│   ├── db/                      # Phase 1: SQLAlchemy models, migrations
│   ├── data/                    # Phase 2: Seeders, fixtures, reference data
│   ├── core/                    # Phase 3: Shared config, settings, utilities
│   ├── agents/                  # Phase 4: LangGraph agents, orchestration
│   │   └── tools/               # Phase 3: Agent tool functions
│   ├── llm/                     # Phase 3: LLM provider abstraction
│   ├── templates/               # Phase 3: Jinja2 briefing templates
│   └── api/                     # Phase 5: FastAPI routes, controllers
│
├── tests/                       # Pytest test suite
├── evals/                       # LLM evaluation suites
├── scripts/                     # Utility/setup scripts
│
├── agents/                      # Agent coordination state (NOT code)
│   ├── CURRENT_STATE.md         # Live project status
│   ├── handoffs/                # Session handoff records
│   └── docs/
│       └── adr/                 # Architecture Decision Records
│
├── .github/
│   ├── workflows/ci.yml         # CI: lint → format-check → test
│   ├── workflows/claude.yml     # Claude Code on @claude mentions
│   └── workflows/claude-code-review.yml
│
├── .claude/
│   └── agents/                  # Claude specialist agent definitions
│
└── .devcontainer/               # VS Code dev container config
```

---

## 4. Environment & Commands

### First-time setup

```bash
cp .env.example .env             # Fill in API keys
uv sync                          # Install all dependencies (dev included)
```

### Common commands

| Action | Command |
|--------|---------|
| Install deps | `uv sync` |
| Run tests | `uv run pytest tests/ -v` |
| Lint | `uv run ruff check src/ tests/` |
| Format check | `uv run ruff format --check src/ tests/` |
| Auto-format | `uv run ruff format src/ tests/` |
| Start app (local) | `uv run uvicorn src.api.main:app --reload --port 8000` |
| Start full stack | `docker compose up` |
| DB only | `docker compose up db` |

### Key environment variables (from `.env.example`)

| Variable | Purpose |
|----------|---------|
| `LLM_PROVIDER` | `openai` or `huggingface` |
| `LLM_MODEL` | Model name (e.g., `gpt-4o-mini`) |
| `OPENAI_API_KEY` | OpenAI credentials |
| `DATABASE_URL` | Async PostgreSQL connection string |
| `EMBEDDING_PROVIDER` | Embedding source (`openai` or `huggingface`) |
| `EMBEDDING_DIMENSION` | Vector dimension (e.g., `1536`) |
| `LANGCHAIN_TRACING_V2` | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | LangSmith credentials |

### CI pipeline (`.github/workflows/ci.yml`)

Runs on push to `main` and all PRs: `ruff check` → `ruff format --check` → `pytest` against a pgvector/pg16 service container. Exit code 5 (no tests collected) is treated as success.

---

## 5. Code Conventions

- **Python 3.12** — use modern syntax (type unions with `|`, `match` statements, etc.)
- **Async-first** — database operations use SQLAlchemy async sessions + asyncpg. Prefer `async def` for any I/O-bound code.
- **Pydantic v2** for all data transfer objects, settings, and request/response models.
- **structlog** for all logging — do not use stdlib `logging` directly.
- **Ruff** enforces style: line-length 100, select rules E (pycodestyle), F (pyflakes), I (isort).
- **Import order** — stdlib → third-party → local (enforced by ruff's `I` rule).
- **Module boundaries** — each `src/` subdirectory is a self-contained module. Cross-module imports should flow downward through the phase dependency chain (db → data → core/tools/llm → agents → api). Never import upward.
- **No new dependencies** without explicitly flagging them for review. The dependency list in `pyproject.toml` is intentional.

---

## 6. Phase Structure

Development proceeds in strict sequential phases. Later phases depend on earlier ones being complete and stable.

### Phase 1 — Schema (`src/db/`)

Database models, SQLAlchemy table definitions, Alembic migrations, pgvector column types.

**Done when:** All tables exist, migrations run cleanly, `CREATE EXTENSION vector` is in init scripts.

### Phase 2 — Seeders (`src/data/`)

Reference data population, fixtures, airport/weather data loaders, HuggingFace dataset integration.

**Done when:** Seed scripts can populate a fresh database with all reference data needed by tools and agents.

### Phase 3 — Tools (`src/core/`, `src/llm/`, `src/agents/tools/`, `src/templates/`)

Shared infrastructure: config/settings (`core`), LLM provider abstraction (`llm`), agent tool functions (`agents/tools`), Jinja2 briefing templates (`templates`), external API clients (weather, NOTAM services).

**Done when:** All tool functions are callable independently, LLM providers are swappable via config, templates render correctly.

### Phase 4 — Agents (`src/agents/`)

LangGraph agent definitions, state graphs, orchestration logic, tool binding, multi-step reasoning chains.

**Done when:** Agents produce correct briefings end-to-end using tools from Phase 3 and data from Phases 1–2.

### Phase 5 — API (`src/api/`)

FastAPI route handlers, request/response schemas, authentication, rate limiting (slowapi), error handling, OpenAPI docs.

**Done when:** All endpoints serve correct responses, rate limiting works, `docker compose up` runs the full stack end-to-end.

### Dependency chain

```
Schema → Seeders → Tools → Agents → API
  1        2        3        4       5
```

Never start work on a phase until all its upstream phases are complete. If blocked by an incomplete upstream phase, stop and report the blocker.

---

## 7. Shared Coordination Architecture

### Source of truth

These four locations are the **only** shared project state. All contributors read and write to them:

| File/Directory | Purpose |
|----------------|---------|
| `AGENTS.md` | Global rules, conventions, workflow (this file) |
| `agents/CURRENT_STATE.md` | Live project status, current phase, blockers, next steps |
| `agents/handoffs/` | Per-session handoff records |
| `agents/docs/adr/` | Architecture Decision Records |

Tool-specific memory (`.claude/*`, Copilot memory, Cursor rules, etc.) is allowed as **secondary context only**. It must never replace or contradict the shared files above.

### Startup checklist (before meaningful work)

1. Read `AGENTS.md` (this file).
2. Read `agents/CURRENT_STATE.md` for current project status.
3. Scan recent files in `agents/handoffs/` for context on recent work.
4. Determine if the task involves an architectural decision → check `agents/docs/adr/`.

### Completion protocol (after meaningful work)

When a session includes meaningful changes (features, fixes, decisions, blockers):

1. **Update** `agents/CURRENT_STATE.md` if project status changed.
2. **Create** a handoff file in `agents/handoffs/` (see §8).
3. **Create or update** an ADR in `agents/docs/adr/` if an architectural decision was made (see §9).

Skip handoffs and ADRs for trivial edits (typo fixes, comment tweaks).

---

## 8. Handoff Protocol

### Filename convention

```
agents/handoffs/YYYY-MM-DD-<contributor>-<short-topic>.md
```

Example: `2026-04-05-sequential-developer-phase1-schema.md`

### Template

```markdown
# Task

[One-line description of the task or goal]

# Completed Work

- [Bullet list of what was accomplished]

# Files Changed

- [List of files created, modified, or deleted]

# Decisions Made

- [Architectural or implementation decisions and rationale]

# Blockers / Risks

- [Anything that blocks progress or needs attention]

# Next Step

- [Clear, actionable recommendation for the next contributor]
```

---

## 9. ADR Protocol

Architecture Decision Records go in `agents/docs/adr/`. Create one when a decision affects project structure, technology choices, or cross-module contracts.

### Filename convention

```
agents/docs/adr/ADR-NNNN-<short-title>.md
```

### Template

```markdown
# ADR-NNNN: [Title]

## Context

[What problem or question prompted this decision?]

## Decision

[What was decided?]

## Why

[Rationale — why this option over alternatives?]

## Consequences

[What changes as a result? What tradeoffs were accepted?]
```

---

## 10. Agent Roster

Specialist agents keep domain-specific behavior in their own config files. All agents must follow the shared coordination workflow defined in this document (§7).

| Agent | Role | Config Location |
|-------|------|-----------------|
| **sequential-developer** | Primary builder. Implements features phase-by-phase in dependency order. Handles all code except tests, docs, and evals. | `.claude/agents/sequential-developer.md` |
| **devops-infrastructure** | Docker, CI/CD, PostgreSQL/pgvector setup, `setup.sh`, end-to-end Docker Compose validation. Active in Phase 1 (parallel) and Phase 5 (finalization). | `.claude/agents/devops-infrastructure.md` |
| **phase-boundary-qa** | Quality gate at phase boundaries. Runs tests, code review, writes and executes eval suites. Invoked only when a phase is declared complete. | `.claude/agents/phase-boundary-qa.md` |
| **mintlify-doc-builder** | Generates and maintains Mintlify MDX documentation from Python source code. | `.claude/agents/mintlify-doc-builder.md` |

### Agent config locations

- **Claude agents:** `.claude/agents/*.md`
- **GitHub Copilot agents:** `.github/agents/*.md`

When adding a new agent, include the shared startup/completion checklist from §7 in its config file.

---

## 11. Core Rules

These apply to **every** contributor — human or AI, regardless of tool:

1. **Read before writing.** Always execute the startup checklist (§7) before meaningful work.
2. **Respect phase order.** Never start a phase until upstream phases are complete (§6).
3. **Minimal, scoped changes.** Do not refactor unrelated code. A bug fix does not need surrounding cleanup.
4. **Follow existing patterns.** Match the conventions established in earlier phases. Do not introduce contradictory abstractions.
5. **No invented requirements.** If requirements are ambiguous, state assumptions explicitly and flag the gap. Do not guess.
6. **No silent new dependencies.** Adding a package to `pyproject.toml` requires explicit justification.
7. **Report after meaningful work.** Update coordination files per the completion protocol (§7).
8. **Module imports flow downward.** `db` → `data` → `core`/`llm`/`tools` → `agents` → `api`. Never import from a higher-phase module.

---

## 12. Security & Secrets

- **Never commit `.env`** — it is gitignored. Use `.env.example` as the template.
- **No hardcoded credentials** in any source file, Dockerfile, or CI config.
- **Database credentials** in `docker-compose.yml` are for local development only. Production must use secret management.
- **Deny patterns** are enforced in `.claude/settings.local.json` to prevent agents from reading `.env`, `.pem`, `.key`, and other sensitive files.
- **CI secrets** (e.g., `CLAUDE_CODE_OAUTH_TOKEN`) are managed via GitHub repository secrets — never echo or log them.
