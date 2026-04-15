"""Authenticated Google API service clients."""

import os
import subprocess
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_SCRIPT = os.path.join(SCRIPT_DIR, "get_token.py")


def _get_token():
    result = subprocess.run(
        [sys.executable, TOKEN_SCRIPT],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr, end="")
        sys.exit(1)
    return result.stdout.strip()


def get_credentials():
    return Credentials(token=_get_token())


def sheets_service():
    return build("sheets", "v4", credentials=get_credentials())


def drive_service():
    return build("drive", "v3", credentials=get_credentials())


def docs_service():
    return build("docs", "v1", credentials=get_credentials())
