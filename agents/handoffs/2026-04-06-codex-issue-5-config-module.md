# Task

Implement Issue `#5` by adding a Pydantic settings-based config module with `.env` loading and a cached accessor.

# Completed Work

- Added `src/core/config.py` with a `Settings` model based on `pydantic-settings`.
- Included the environment variables requested in Issue `#5` plus the existing Hugging Face/OpenAI-related keys already present in `.env.example`.
- Added cached `get_settings()` access.
- Updated DB modules and tests to consume centralized settings values instead of reaching directly into ad hoc environment lookups for embedding configuration.
- Recorded that this work proceeded under an explicit user-approved exception to the normal phase-order gate.

# Files Changed

- `src/core/config.py`
- `src/db/connection.py`
- `src/db/models.py`
- `tests/test_config.py`
- `tests/test_db_models.py`
- `agents/CURRENT_STATE.md`
- `agents/handoffs/2026-04-06-codex-issue-5-config-module.md`

# Decisions Made

- Kept secrets and `DATABASE_URL` nullable in `Settings` so importing configuration does not require every environment variable to exist at all times.
- Left `src.db.connection` responsible for enforcing that `DATABASE_URL` is present before DB connectivity is initialized.
- Reused the centralized settings object for embedding dimension so DB models and tests stay aligned with configuration.

# Blockers / Risks

- This issue is Phase 3 work under `AGENTS.md`, but it was implemented before Phase 2 completion under explicit user direction.
- Full integration testing still depends on a live PostgreSQL/pgvector environment.

# Next Step

- Run targeted tests for the config module and DB smoke tests in an environment with project dependencies and the test database available.
