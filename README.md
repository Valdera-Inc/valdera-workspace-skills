# Google Auth Plugin for Claude Code

A Claude Code plugin that gives agents access to Google APIs (Sheets, Drive, Docs, Gmail) via OAuth. Handles credential setup, browser-based authentication, token caching, and automatic refresh — all with zero external dependencies.

## Install

```
/plugin marketplace add valdera/oauth-store
/plugin install google-auth@valdera-tools
```

Or add to any project's `.claude/settings.json` to auto-prompt teammates:

```json
{
  "extraKnownMarketplaces": {
    "valdera-tools": {
      "source": { "source": "github", "repo": "valdera/oauth-store" }
    }
  },
  "enabledPlugins": {
    "google-auth@valdera-tools": true
  }
}
```

## How it works

Once installed, the agent can call `/google-auth` or use the skill automatically whenever a task involves Google APIs. Under the hood it runs `token.py`, which:

1. **First run** — prompts the user to paste OAuth client credentials (from a shared internal doc) and sign in via the browser. Tokens are saved to `~/.oauth-store/`.
2. **Subsequent runs** — returns a cached access token instantly, refreshing it automatically if expired.

The token is printed to stdout; the agent uses it as a `Bearer` token in Google API calls.

## Scopes

The token grants access to:

- **Google Sheets** — read/write
- **Google Drive** — read/write
- **Google Docs** — read/write
- **Gmail** — read-only

## Requirements

- macOS with `python3` (ships with Xcode Command Line Tools)
- Claude Code CLI
- Access to the shared OAuth credentials doc (Valdera internal)

## Repo structure

```
oauth-store/
├── .claude-plugin/
│   └── marketplace.json              # marketplace catalog
└── plugins/
    └── google-auth/
        ├── .claude-plugin/
        │   └── plugin.json           # plugin manifest
        └── skills/
            └── google-auth/
                ├── SKILL.md           # agent instructions + API examples
                └── scripts/
                    └── token.py       # OAuth script (stdlib only)
```
