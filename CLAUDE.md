# Valdera Workspace Skills

Google Workspace tools for Claude Code — Sheets, Drive, and Docs.

## Authentication

All scripts authenticate via `scripts/get_token.py`, which reads `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from the `.env` file in the project root. Tokens are cached at `~/.oauth-store/tokens.json` and refresh automatically.

**First run requires user interaction** — the script opens a browser for Google sign-in. Always ask the user before running a script for the first time:

> I need to access Google APIs. This will open your browser for sign-in. Ready?

If auth fails with a refresh error, delete `~/.oauth-store/tokens.json` and re-run.

## Running scripts

Always use `uv run` to run scripts. Never use bare `python3` — it won't have the dependencies.

## Available skills

- **google-sheets** — `scripts/sheets.py`: read, write, append, info
- **google-drive** — `scripts/drive.py`: list, search, download, export, upload
- **google-docs** — `scripts/docs.py`: read (plain text), json (raw API)

## Writing custom scripts

Use `scripts/google_client.py` for authenticated service clients:

```python
from scripts.google_client import sheets_service, drive_service, docs_service
```

Google SDK dependencies are already in `pyproject.toml`.
