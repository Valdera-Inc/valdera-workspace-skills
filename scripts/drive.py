#!/usr/bin/env python3
"""Google Drive CLI. Outputs JSON to stdout.

Usage:
  uv run scripts/drive.py list  [QUERY]
  uv run scripts/drive.py search NAME
  uv run scripts/drive.py download FILE_ID [OUTPUT_PATH]
  uv run scripts/drive.py export FILE_ID MIME_TYPE [OUTPUT_PATH]
  uv run scripts/drive.py upload LOCAL_PATH [PARENT_FOLDER_ID]
"""

import io
import json
import mimetypes
import os
import sys

from google_client import drive_service
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


def list_files(query=None):
    svc = drive_service()
    params = {"fields": "files(id,name,mimeType,modifiedTime)", "pageSize": 100}
    if query:
        params["q"] = query
    result = svc.files().list(**params).execute()
    print(json.dumps(result.get("files", []), indent=2))


def search(name):
    list_files(f"name contains '{name}' and trashed=false")


def download(file_id, output_path=None):
    svc = drive_service()
    if not output_path:
        meta = svc.files().get(fileId=file_id, fields="name").execute()
        output_path = meta["name"]
    request = svc.files().get_media(fileId=file_id)
    with io.FileIO(output_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    print(json.dumps({"downloaded": output_path}))


def export(file_id, mime_type, output_path=None):
    svc = drive_service()
    if not output_path:
        meta = svc.files().get(fileId=file_id, fields="name").execute()
        ext = mimetypes.guess_extension(mime_type) or ""
        output_path = meta["name"] + ext
    request = svc.files().export_media(fileId=file_id, mimeType=mime_type)
    with io.FileIO(output_path, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
    print(json.dumps({"exported": output_path}))


def upload(local_path, parent_id=None):
    svc = drive_service()
    name = os.path.basename(local_path)
    mime, _ = mimetypes.guess_type(local_path)
    body = {"name": name}
    if parent_id:
        body["parents"] = [parent_id]
    media = MediaFileUpload(local_path, mimetype=mime or "application/octet-stream")
    result = svc.files().create(body=body, media_body=media, fields="id,name").execute()
    print(json.dumps(result))


def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    if sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "list":
        list_files(args[0] if args else None)
    elif cmd == "search" and len(args) == 1:
        search(args[0])
    elif cmd == "download" and 1 <= len(args) <= 2:
        download(args[0], args[1] if len(args) > 1 else None)
    elif cmd == "export" and 2 <= len(args) <= 3:
        export(args[0], args[1], args[2] if len(args) > 2 else None)
    elif cmd == "upload" and 1 <= len(args) <= 2:
        upload(args[0], args[1] if len(args) > 1 else None)
    else:
        print(__doc__, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
