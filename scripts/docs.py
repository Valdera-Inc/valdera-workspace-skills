#!/usr/bin/env python3
"""Google Docs CLI. Outputs plain text or JSON to stdout.

Usage:
  python3 scripts/docs.py read DOCUMENT_ID
  python3 scripts/docs.py json DOCUMENT_ID
"""

import json
import sys

from google_client import docs_service


def _extract_text(doc):
    """Extract plain text from Docs API structured response."""
    parts = []
    for element in doc.get("body", {}).get("content", []):
        paragraph = element.get("paragraph")
        if not paragraph:
            continue
        for run in paragraph.get("elements", []):
            text = run.get("textRun", {}).get("content", "")
            if text:
                parts.append(text)
    return "".join(parts)


def read(document_id):
    doc = docs_service().documents().get(documentId=document_id).execute()
    print(_extract_text(doc))


def read_json(document_id):
    doc = docs_service().documents().get(documentId=document_id).execute()
    print(json.dumps(doc, indent=2))


def main():
    if len(sys.argv) < 3:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]
    doc_id = sys.argv[2]

    if cmd == "read":
        read(doc_id)
    elif cmd == "json":
        read_json(doc_id)
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
