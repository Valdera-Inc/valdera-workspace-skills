---
name: google-auth
description: Get OAuth access tokens for Google APIs — Sheets, Drive, Docs, Gmail, and more. Use this skill whenever a task involves reading or writing Google Sheets, listing or downloading files from Google Drive, reading or editing Google Docs, or reading Gmail. If a task requires calling any Google API, use this skill to get a valid token first.
---

# Google Auth

Provides a valid Google OAuth access token. The script handles browser-based authentication, token caching, and automatic refresh. The token grants access to Sheets, Drive, Docs, and Gmail (read-only).

## Prerequisites

The project requires a `.env` file in the repo root with Google OAuth client credentials:

```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

If `.env` is missing or incomplete, the script will exit with an error telling the user to set it up.

## Getting a token

```bash
TOKEN=$(python3 scripts/get_token.py)
```

The `get_token.py` script lives at `scripts/get_token.py` in the repo root.

The token is printed to stdout. All prompts and status messages go to stderr, so `$TOKEN` will always be just the access token string.

### First run

On first run, the script opens the user's browser for Google sign-in. After sign-in, tokens are saved to `~/.oauth-store/`.

**Before running `get_token.py` for the first time**, tell the user something like:

> I need to authenticate with Google. This will open your browser for sign-in. Ready?

Wait for the user to confirm before proceeding.

### Subsequent runs

The script returns immediately with a cached token. If the token is expired, it refreshes automatically via the saved refresh token — no user interaction needed.

## Using the token

Fetch a fresh token before each API call (the script handles caching internally):

```bash
TOKEN=$(python3 scripts/get_token.py)
```

---

## Google Sheets API

### Read cell values

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/RANGE"
```

- `SPREADSHEET_ID` is the long ID in the sheet URL: `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`
- `RANGE` uses A1 notation, e.g. `Sheet1!A1:D10` or just `Sheet1` for all data

### Get spreadsheet metadata

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID?fields=sheets.properties"
```

### Write cell values

```bash
curl -s -X PUT -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/RANGE?valueInputOption=USER_ENTERED" \
  -d '{"values": [["row1col1", "row1col2"], ["row2col1", "row2col2"]]}'
```

### Append rows

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://sheets.googleapis.com/v4/spreadsheets/SPREADSHEET_ID/values/RANGE:append?valueInputOption=USER_ENTERED" \
  -d '{"values": [["val1", "val2"]]}'
```

---

## Google Drive API

### List files

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/drive/v3/files?q=name%20contains%20'report'&fields=files(id,name,mimeType)"
```

Common query filters: `mimeType='application/vnd.google-apps.spreadsheet'`, `'FOLDER_ID' in parents`, `trashed=false`.

### Download a file

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/drive/v3/files/FILE_ID?alt=media" -o output.dat
```

For Google-native formats (Docs, Sheets), export instead:

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/drive/v3/files/FILE_ID/export?mimeType=text/csv" -o output.csv
```

### Upload a file

```bash
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart" \
  -F "metadata={\"name\": \"report.csv\"};type=application/json" \
  -F "file=@report.csv;type=text/csv"
```

---

## Google Docs API

### Get document content

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://docs.googleapis.com/v1/documents/DOCUMENT_ID"
```

The `DOCUMENT_ID` is in the doc URL: `https://docs.google.com/document/d/DOCUMENT_ID/edit`

### Get plain text only

The Docs API returns structured JSON. To extract plain text, parse the `body.content` array for `textRun` elements, or export via Drive:

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://www.googleapis.com/drive/v3/files/DOCUMENT_ID/export?mimeType=text/plain"
```

---

## Gmail API (read-only)

### List recent messages

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=10"
```

### Read a message

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages/MESSAGE_ID?format=full"
```

### Search messages

```bash
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://gmail.googleapis.com/gmail/v1/users/me/messages?q=from:someone@example.com+after:2025/01/01"
```

---

## For more complex tasks, use the Google Python SDKs

The curl examples above work well for simple reads and writes. For more sophisticated work — batch updates, formatting, complex queries, pagination, error handling — write a Python script using the official Google client libraries instead.

The Google SDK dependencies are already included in this project's `pyproject.toml`. Use the token from `get_token.py` to build an authenticated client:

```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import subprocess

token = subprocess.check_output(["python3", "scripts/get_token.py"]).decode().strip()
creds = Credentials(token=token)

# Sheets
sheets = build("sheets", "v4", credentials=creds)

# Drive
drive = build("drive", "v3", credentials=creds)

# Docs
docs = build("docs", "v1", credentials=creds)

# Gmail
gmail = build("gmail", "v1", credentials=creds)
```

This is the preferred approach for anything beyond simple CRUD — batch operations, complex formatting, multi-step workflows, etc.

---

## Troubleshooting

If the token command fails with a refresh error, the saved tokens may be stale. Delete them and re-authenticate:

```bash
rm ~/.oauth-store/tokens.json
TOKEN=$(python3 scripts/get_token.py)
```

This will re-trigger the browser sign-in flow (requires user interaction).
