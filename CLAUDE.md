# Valdera Workspace Skills

The purpose of this repo is to provide tools and scripts for data exploration.

## Authentication

All scripts authenticate via `scripts/get_token.py`, which reads `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from the `.env` file in the project root. Tokens are cached at `~/.oauth-store/tokens.json` and refresh automatically.

**First run requires user interaction** — the script opens a browser for Google sign-in. Always ask the user before running a script for the first time:

> I need to access Google APIs. This will open your browser for sign-in. Ready?

If auth fails with a refresh error, delete `~/.oauth-store/tokens.json` and re-run.

## Running scripts

Always use `uv run` to run scripts. Never use bare `python3` — it won't have the dependencies.

## Available scripts

- **google-sheets** — `scripts/sheets.py`: read, write, append, info
- **google-drive** — `scripts/drive.py`: list, search, download, export, upload
- **google-docs** — `scripts/docs.py`: read (plain text), json (raw API)
- **bigquery** — `scripts/bigquery.py`: query, list-datasets, list-tables, table-info
- **gmail** — `scripts/gmail.py`: profile, search, read, threads, thread, list-labels, create-label, delete-label, label, trash/untrash, draft, send, attachment

## Advanced analysis with custom scripts

For more complex analysis, create a new folder under $PROJECT_ROOT/analysis/. Name the folder something easy to recognize based on the general content of the session so far. Or ask the user for a session name if it's not clear. 

Prefer to write a python script in the analysis folder over executing scripts directly with the "-c" flag. Import functions from existing scripts where reasonable to do so. Importing from google_client.py should almost always be preferrerd, since it manages the auth as well.

## Project memory (MEMORY.md)

Maintain a `MEMORY.md` file at the project root for facts learned across sessions. **Read it at the start of every session** and **update it when you learn something worth persisting**.

What to store:
- Identifiers the user provides in response to a question — GCP project IDs, dataset IDs, spreadsheet IDs, doc IDs, etc. Record what the ID is for so you can reuse it next time instead of asking again.
- Conventions or preferences the user states explicitly (e.g. "always use dataset X for Y analysis").
- Non-obvious facts about data sources — schema quirks, which tables are stale, which project owns which dataset.

What NOT to store:
- Anything already in CLAUDE.md, the code, or `.env`.
- Ephemeral task state or conversation context.

Format: plain markdown with short bullets under topical headings (e.g. `## BigQuery`, `## Sheets`). Update in place rather than appending chronologically. If a stored fact turns out to be wrong, correct or remove it.
