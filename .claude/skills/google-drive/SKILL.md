---
name: google-drive
description: List, search, download, upload, and export files in Google Drive. Use when a task involves finding files, downloading content, or uploading results.
---

# Google Drive

CLI at `scripts/drive.py`. Requires auth via `scripts/get_token.py` (handled automatically).

## Commands

### List files

```bash
uv run scripts/drive.py list
uv run scripts/drive.py list "mimeType='application/vnd.google-apps.spreadsheet'"
```

The optional argument is a Drive API query string. Returns JSON array of `{id, name, mimeType, modifiedTime}`.

### Search by name

```bash
uv run scripts/drive.py search 'quarterly report'
```

### Download a file

```bash
uv run scripts/drive.py download FILE_ID
uv run scripts/drive.py download FILE_ID output.pdf
```

For binary files (PDFs, images, etc). Defaults to the file's original name.

### Export Google-native files

```bash
uv run scripts/drive.py export DOCUMENT_ID text/plain
uv run scripts/drive.py export SPREADSHEET_ID text/csv output.csv
```

Use for Docs, Sheets, Slides. Common MIME types: `text/plain`, `text/csv`, `application/pdf`.

### Upload a file

```bash
uv run scripts/drive.py upload report.csv
uv run scripts/drive.py upload report.csv PARENT_FOLDER_ID
```

## First run

On first run, the user will be prompted to authenticate via browser. Tell them before running:

> I need to access Google Drive. This will open your browser for sign-in. Ready?

## For complex operations

For batch operations or folder management, write a Python script using `google_client.py`:

```python
from scripts.google_client import drive_service
svc = drive_service()
```
