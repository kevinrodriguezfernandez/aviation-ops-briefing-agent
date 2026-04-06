# Current Project State

Last updated: 2026-04-06

## Current Phase

Pre-Phase 1. All `src/` modules are scaffolded (empty `__init__.py` files) but no application code exists yet. Infrastructure (Docker, CI, devcontainer) is in place.

## Coordination Baseline

- `AGENTS.md` rewritten as the comprehensive, tool-agnostic coordination document — includes project overview, tech stack, repository map, environment commands, code conventions, expanded phase structure, handoff/ADR templates, agent roster, core rules, and security guidance.
- Shared coordination architecture standardized around:
  - `AGENTS.md` (global rules and workflow)
  - `agents/CURRENT_STATE.md` (this file — live project status)
  - `agents/handoffs/` (session handoff records)
  - `docs/adr/` (architecture decision records)
- ADR created: `docs/adr/ADR-0001-shared-agent-coordination.md`

## Agent Definitions

- Specialist agent definitions live in:
  - `.claude/agents/` — sequential-developer, devops-infrastructure, phase-boundary-qa, mintlify-doc-builder
  - `.github/agents/` — currently empty (tester.agent.md referenced in handoff but file missing)
- All agent configs include the shared startup/completion checklist from `AGENTS.md` §7.

## Infrastructure Status

- **Docker**: `Dockerfile` (python:3.12-slim, uv, non-root user) + `docker-compose.yml` (app + pgvector/pg16) ready
- **CI**: `.github/workflows/ci.yml` runs lint → format-check → test on push/PR
- **Claude GitHub workflows**:
  - `.github/workflows/claude.yml` remains mention-driven (`@claude`)
  - `.github/workflows/claude-code-review.yml` now runs manually via `workflow_dispatch` with a PR number input to avoid automatic token usage on every PR update
- **Devcontainer**: `.devcontainer/` configured with Docker-in-Docker, Python + Ruff extensions, uv sync on create

## Open Risks / Watch Items

- `.github/agents/tester.agent.md` referenced in handoff but does not exist — needs to be created or removed from references.
- Future agent additions should include the shared startup/completion checklists from `AGENTS.md` §7.
- Keep tool-specific memory as secondary guidance only; repo-visible files are the source of truth.
- Issue `#5` (`src/core/config.py`) is being implemented under an explicit user-approved exception to the normal phase gate in `AGENTS.md`; Phase 2 remains incomplete.

## Next Recommended Step

- Begin Phase 1 (Schema): define SQLAlchemy models and migrations in `src/db/`.
