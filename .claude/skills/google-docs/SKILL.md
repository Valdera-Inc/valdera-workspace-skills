---
name: google-docs
description: Read Google Docs content as plain text. Use when a task involves reading or referencing a Google Doc.
---

# Google Docs

CLI at `scripts/docs.py`. Requires auth via `scripts/get_token.py` (handled automatically).

## Commands

### Read as plain text

```bash
uv run scripts/docs.py read DOCUMENT_ID
```

Extracts and prints the document's text content. The document ID is in the URL: `docs.google.com/document/d/DOCUMENT_ID/edit`

### Read as raw JSON

```bash
uv run scripts/docs.py json DOCUMENT_ID
```

Returns the full Docs API response with structural elements (paragraphs, formatting, etc).

## First run

On first run, the user will be prompted to authenticate via browser. Tell them before running:

> I need to access Google Docs. This will open your browser for sign-in. Ready?

## For complex operations

For creating or editing docs, write a Python script using `google_client.py`:

```python
from scripts.google_client import docs_service
svc = docs_service()
```
