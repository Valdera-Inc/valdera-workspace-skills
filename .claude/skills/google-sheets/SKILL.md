---
name: google-sheets
description: Read, write, and append data in Google Sheets. Use when a task involves spreadsheet data — reading values, writing results, or appending rows.
---

# Google Sheets

CLI at `scripts/sheets.py`. Requires auth via `scripts/get_token.py` (handled automatically).

## Commands

### Read cells

```bash
uv run scripts/sheets.py read SPREADSHEET_ID 'Sheet1!A1:D10'
```

Returns JSON array of rows: `[["a","b"],["c","d"]]`

Use just `Sheet1` for all data. The spreadsheet ID is the long string in the URL: `docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`

### Write cells

```bash
uv run scripts/sheets.py write SPREADSHEET_ID 'Sheet1!A1' '[["a","b"],["c","d"]]'
```

Third argument is a JSON array of rows.

### Append rows

```bash
uv run scripts/sheets.py append SPREADSHEET_ID 'Sheet1' '[["new","row"]]'
```

Appends after the last row with data.

### Spreadsheet info

```bash
uv run scripts/sheets.py info SPREADSHEET_ID
```

Returns title and sheet names/properties.

## First run

On first run, the user will be prompted to authenticate via browser. Tell them before running:

> I need to access Google Sheets. This will open your browser for sign-in. Ready?

## For complex operations

For batch updates, conditional formatting, or multi-step workflows, write a Python script using `google_client.py`:

```python
from scripts.google_client import sheets_service
svc = sheets_service()
```
