#!/usr/bin/env python3
"""Google BigQuery CLI. Outputs JSON to stdout.

Usage:
  uv run scripts/bigquery.py query         SQL
  uv run scripts/bigquery.py list-datasets PROJECT_ID
  uv run scripts/bigquery.py list-tables   PROJECT_ID DATASET_ID
  uv run scripts/bigquery.py table-info    PROJECT_ID DATASET_ID TABLE_ID

Billing project is read from PROJECT_ID in .env (used by `query`). The
PROJECT_ID argument to list-datasets/list-tables/table-info is the project that
*owns* the datasets being inspected.
"""

import json
import os
import sys

from get_token import _load_env
from google_client import bigquery_service


def _billing_project():
    pid = _load_env().get("PROJECT_ID") or os.environ.get("PROJECT_ID")
    if not pid:
        print("Error: PROJECT_ID must be set in .env", file=sys.stderr)
        sys.exit(1)
    return pid


def _coerce(value, field_type):
    if value is None:
        return None
    t = field_type.upper()
    if t in ("INTEGER", "INT64"):
        return int(value)
    if t in ("FLOAT", "FLOAT64", "NUMERIC", "BIGNUMERIC"):
        return float(value)
    if t in ("BOOLEAN", "BOOL"):
        return value == "true"
    return value


def _rows_to_dicts(schema_fields, rows):
    out = []
    for row in rows:
        cells = row["f"]
        out.append(
            {
                field["name"]: _coerce(cell["v"], field["type"])
                for field, cell in zip(schema_fields, cells)
            }
        )
    return out


def query(sql):
    result = (
        bigquery_service()
        .jobs()
        .query(
            projectId=_billing_project(),
            body={"query": sql, "useLegacySql": False},
        )
        .execute()
    )

    schema_fields = result["schema"]["fields"]
    rows = _rows_to_dicts(schema_fields, result["rows"])
    print(
        json.dumps(
            {
                "totalRows": int(result["totalRows"]),
                "rows": rows,
            },
            indent="\t",
        )
    )


def list_datasets(project_id):
    result = bigquery_service().datasets().list(projectId=project_id).execute()
    print(json.dumps(result["datasets"], indent="\t"))


def list_tables(project_id, dataset_id):
    result = (
        bigquery_service()
        .tables()
        .list(
            projectId=project_id,
            datasetId=dataset_id,
        )
        .execute()
    )
    print(json.dumps(result["tables"], indent="\t"))


def table_info(project_id, dataset_id, table_id):
    result = (
        bigquery_service()
        .tables()
        .get(
            projectId=project_id,
            datasetId=dataset_id,
            tableId=table_id,
        )
        .execute()
    )
    print(json.dumps(result, indent="\t"))


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "query" and len(args) == 1:
        query(args[0])
    elif cmd == "list-datasets" and len(args) == 1:
        list_datasets(args[0])
    elif cmd == "list-tables" and len(args) == 2:
        list_tables(args[0], args[1])
    elif cmd == "table-info" and len(args) == 3:
        table_info(args[0], args[1], args[2])
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
