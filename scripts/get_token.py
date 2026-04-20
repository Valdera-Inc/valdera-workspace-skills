#!/usr/bin/env python3
"""
oauth-store: Google OAuth token manager.

Usage: python3 token.py

Prints a valid Google OAuth access token to stdout.
On first run, opens the browser for Google sign-in.
All prompts and status messages go to stderr so stdout is always just the token.

Requires GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in a .env file
at the project root (next to pyproject.toml).
"""

import base64
import hashlib
import http.server
import json
import os
import secrets
import sys
import time
import urllib.parse
import urllib.request
import webbrowser

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
ENV_FILE = os.path.join(PROJECT_ROOT, ".env")

TOKENS_FILE = os.path.join(os.path.expanduser("~/.oauth-store"), "tokens.json")

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/bigquery",
]
REDIRECT_PORT = 8085
REDIRECT_URI = f"http://localhost:{REDIRECT_PORT}"

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def _info(msg):
    """Print informational message to stderr."""
    print(msg, file=sys.stderr, flush=True)


def _load_env():
    """Parse the .env file and return a dict of key=value pairs."""
    env = {}
    if not os.path.exists(ENV_FILE):
        return env
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            key, _, value = line.partition("=")
            env[key.strip()] = value.strip()
    return env


# ---------------------------------------------------------------------------
# Credentials (client ID / secret from .env)
# ---------------------------------------------------------------------------

def load_credentials():
    """Load client credentials from the .env file."""
    env = _load_env()
    client_id = env.get("GOOGLE_CLIENT_ID", "")
    client_secret = env.get("GOOGLE_CLIENT_SECRET", "")

    if not client_id or not client_secret:
        _info("Error: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env")
        _info(f"Expected .env location: {ENV_FILE}")
        sys.exit(1)

    return {"client_id": client_id, "client_secret": client_secret}


# ---------------------------------------------------------------------------
# Tokens (access / refresh)
# ---------------------------------------------------------------------------

def load_tokens():
    """Load saved tokens, or return None."""
    if not os.path.exists(TOKENS_FILE):
        return None
    with open(TOKENS_FILE) as f:
        return json.load(f)


def save_tokens(tokens):
    os.makedirs(os.path.dirname(TOKENS_FILE), exist_ok=True)
    with open(TOKENS_FILE, "w") as f:
        json.dump(tokens, f, indent=2)
    os.chmod(TOKENS_FILE, 0o600)


def is_expired(tokens):
    """True if the access token is expired or will expire within 5 minutes."""
    obtained_at = tokens.get("obtained_at", 0)
    expires_in = tokens.get("expires_in", 0)
    return time.time() > (obtained_at + expires_in - 300)


def refresh_access_token(tokens, creds):
    """Use the refresh token to get a new access token. Returns updated tokens or None."""
    if "refresh_token" not in tokens:
        return None

    data = urllib.parse.urlencode({
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "refresh_token": tokens["refresh_token"],
        "grant_type": "refresh_token",
    }).encode()

    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req) as resp:
            new = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        _info(f"Token refresh failed: {e.read().decode()}")
        return None

    tokens["access_token"] = new["access_token"]
    tokens["expires_in"] = new["expires_in"]
    tokens["obtained_at"] = int(time.time())
    if "refresh_token" in new:
        tokens["refresh_token"] = new["refresh_token"]

    save_tokens(tokens)
    return tokens


# ---------------------------------------------------------------------------
# OAuth browser flow
# ---------------------------------------------------------------------------

def run_auth_flow(creds):
    """Open the browser for Google sign-in, capture the token via localhost redirect."""
    code_verifier = secrets.token_urlsafe(64)
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b"=").decode()

    state = secrets.token_urlsafe(32)

    params = {
        "client_id": creds["client_id"],
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }

    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    auth_code = [None]
    auth_error = [None]

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

            if qs.get("state", [None])[0] != state:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"State mismatch. Please try again.")
                return

            if "code" in qs:
                auth_code[0] = qs["code"][0]
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(
                    b"<h1>Authentication successful!</h1>"
                    b"<p>You can close this tab.</p>"
                )
            else:
                auth_error[0] = qs.get("error", ["unknown"])[0]
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(f"<h1>Error: {auth_error[0]}</h1>".encode())

        def log_message(self, format, *args):
            pass  # suppress request logs

    server = http.server.HTTPServer(("localhost", REDIRECT_PORT), CallbackHandler)

    _info("Opening browser for Google sign-in...")
    _info(f"If it doesn't open, visit:\n  {auth_url}\n")
    webbrowser.open(auth_url)

    server.handle_request()
    server.server_close()

    if auth_error[0]:
        _info(f"Authentication failed: {auth_error[0]}")
        sys.exit(1)
    if not auth_code[0]:
        _info("Authentication failed: no authorization code received.")
        sys.exit(1)

    # Exchange authorization code for tokens
    data = urllib.parse.urlencode({
        "code": auth_code[0],
        "client_id": creds["client_id"],
        "client_secret": creds["client_secret"],
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
        "code_verifier": code_verifier,
    }).encode()

    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")

    try:
        with urllib.request.urlopen(req) as resp:
            tokens = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        _info(f"Token exchange failed: {e.read().decode()}")
        sys.exit(1)

    tokens["obtained_at"] = int(time.time())
    save_tokens(tokens)
    _info("Authentication successful!\n")
    return tokens


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    creds = load_credentials()
    tokens = load_tokens()

    if tokens is None or "refresh_token" not in tokens:
        tokens = run_auth_flow(creds)
        print(tokens["access_token"])
        return

    if not is_expired(tokens):
        print(tokens["access_token"])
        return

    refreshed = refresh_access_token(tokens, creds)
    if refreshed:
        print(refreshed["access_token"])
        return

    _info("Refresh failed, re-authenticating...")
    tokens = run_auth_flow(creds)
    print(tokens["access_token"])


if __name__ == "__main__":
    main()
