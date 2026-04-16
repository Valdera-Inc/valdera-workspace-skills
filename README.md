# Valdera Workspace Skills

Scripts and skills that let Claude Code agents work with Google Sheets, Drive, and Docs.

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Valdera-Inc/valdera-workspace-skills.git
cd valdera-workspace-skills
```

### 2. Install Python dependencies

This project uses [uv](https://docs.astral.sh/uv/). If you don't have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then install dependencies:

```bash
uv sync
```

### 3. Set up your `.env` file

Copy the example and fill in your Google OAuth credentials:

```bash
cp .env.example .env
```

Open `.env` in a text editor and paste your Client ID and Client Secret:

```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

Ask your team lead for these values, or get them from your Google Cloud Console under **APIs & Credentials > OAuth 2.0 Client IDs**.

### 4. Sign in with Google

The first time you run any script, it will open your browser to sign in with Google. After that, tokens are cached and refresh automatically.

## Using with Claude Code

Open this folder in Claude Code and the skills are available automatically. Just ask Claude to do things like:

- "Read the data from this spreadsheet: https://docs.google.com/spreadsheets/d/..."
- "Find the quarterly report on my Drive"
- "What does this doc say? https://docs.google.com/document/d/..."

Claude will pick the right script and handle authentication. The first time, it will ask you to sign in via your browser.
