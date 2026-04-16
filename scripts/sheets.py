#!/usr/bin/env python3
"""Google Sheets CLI. Outputs JSON to stdout.

Usage:
  uv run scripts/sheets.py read  SPREADSHEET_ID RANGE
  uv run scripts/sheets.py write SPREADSHEET_ID RANGE '[["a","b"],["c","d"]]'
  uv run scripts/sheets.py append SPREADSHEET_ID RANGE '[["a","b"]]'
  uv run scripts/sheets.py info  SPREADSHEET_ID
"""

import json
import sys

from google_client import sheets_service


def read(spreadsheet_id, range_):
    result = sheets_service().spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_,
    ).execute()
    print(json.dumps(result.get("values", []), indent=2))


def write(spreadsheet_id, range_, data_json):
    values = json.loads(data_json)
    result = sheets_service().spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_,
        valueInputOption="USER_ENTERED", body={"values": values},
    ).execute()
    print(json.dumps({"updatedCells": result.get("updatedCells", 0)}))


def append(spreadsheet_id, range_, data_json):
    values = json.loads(data_json)
    result = sheets_service().spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range_,
        valueInputOption="USER_ENTERED", body={"values": values},
    ).execute()
    print(json.dumps({"updatedCells": result.get("updates", {}).get("updatedCells", 0)}))


def info(spreadsheet_id):
    result = sheets_service().spreadsheets().get(
        spreadsheetId=spreadsheet_id, fields="properties.title,sheets.properties",
    ).execute()
    print(json.dumps(result, indent=2))


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "read" and len(args) == 2:
        read(args[0], args[1])
    elif cmd == "write" and len(args) == 3:
        write(args[0], args[1], args[2])
    elif cmd == "append" and len(args) == 3:
        append(args[0], args[1], args[2])
    elif cmd == "info" and len(args) == 1:
        info(args[0])
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
