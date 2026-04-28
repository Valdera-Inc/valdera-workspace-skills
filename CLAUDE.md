# Valdera Workspace Skills

This project provides tools and scripts for data exploration.

## User sophistication
Assume that the users are totally non technical unless they say "ABRACADABRA". For the default user:

- Do not make any changes to any of the commited files. All changes must go into a subproject (explained below)
- When they start a conversation, refresh the repo to the latest main with a git pull
- If they don't have a .env file, ask them to paste the contents and then you create the .env for them

If a user does say ABRACADABRA, assume they are developers and let them do what they want


## Authentication
All scripts authenticate via `scripts/get_token.py`, which reads `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from the `.env` file in the project root. Tokens are cached at `~/.oauth-store/tokens.json` and refresh automatically. **First run requires user interaction** — the script opens a browser for Google sign-in. Let the user know.

If auth fails with a refresh error, delete `~/.oauth-store/tokens.json` and re-run.

## Running scripts

Always use `uv run` to run scripts. Never use bare `python3` — it won't have the dependencies.

## Available scripts

- **google-sheets** — `scripts/sheets.py`: read, write, append, info
- **google-drive** — `scripts/drive.py`: list, search, download, export, upload
- **google-docs** — `scripts/docs.py`: read (plain text), json (raw API)
- **bigquery** — `scripts/bigquery.py`: query, list-datasets, list-tables, table-info
- **gmail** — `scripts/gmail.py`: profile, search, read, threads, thread, list-labels, create-label, delete-label, label, trash/untrash, draft, send, attachment

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

## Subprojects

For anything that goes beyond very basic answers, create a project for the user under the `projects` directory. Maintain the following structure:

projects/
  README.md
  <project_name>/
    README.md
    scripts/
    artifacts/

Liberally create scripts under the project scripts folder rather than relying on ad-hoc shell invocations. Any artifacts (spreadsheets, presentations, graphs, etc.) go under the artifacts directory. Keep updating the project README as you go.
