---
description: Pull/sync custom skills and commands from the claude-skills GitHub repository
allowed-tools: [Bash, Read, Write, Glob, Grep]
---

# Sync Custom Skills & Commands from GitHub

Pull the latest custom skills and commands from the `claude-skills` GitHub repository into `~/.claude/skills/` and `~/.claude/commands/`.

The GitHub repo uses a structured layout: skills are under `skills/`, commands are under `commands/`.

## Important: Temp Clone Approach

Do NOT create or maintain a git repo inside `~/.claude/skills/`. Instead, clone to a temporary directory, then copy files to their local destinations. This keeps the local directory clean.

## Instructions

Execute the following steps in order. Use Bash for all commands.

### Step 1: Detect OS and find `gh` CLI

1. Detect the OS:
   ```
   uname -s
   ```
   - `MINGW*` or `MSYS*` = Windows (Git Bash)
   - `Darwin` = macOS
   - `Linux` = Linux

2. Find `gh` CLI — try these in order:
   ```
   command -v gh 2>/dev/null
   ```
   - If found, use it directly
   - If NOT found on **Windows**: check `/tmp/gh/bin/gh.exe`. If that also doesn't exist, download the portable version:
     ```
     curl -sL https://github.com/cli/cli/releases/latest/download/gh_<VERSION>_windows_amd64.zip -o /tmp/gh.zip
     unzip -o /tmp/gh.zip -d /tmp/gh
     ```
     Then use `/tmp/gh/bin/gh.exe` as the `gh` command for all subsequent steps.
     To find the latest version, run: `curl -sI https://github.com/cli/cli/releases/latest | grep -i location | grep -oP 'v[\d.]+'` or hardcode a recent version.
   - If NOT found on **macOS**: run `brew install gh` (if `brew` not available, tell the user to install Homebrew and stop)
   - If NOT found on **Linux**: tell the user to install `gh` via their package manager and stop

3. Store the working `gh` path in a variable (e.g., `GH_CMD`) for all subsequent steps.

4. Check authentication: `$GH_CMD auth status`
   - If not authenticated, tell the user the full path to run `gh auth login` (use `cygpath -w` on Windows to show the Windows path) and stop

5. Get the GitHub username: `$GH_CMD api user --jq '.login'`

### Step 2: Clone repo to temp directory

1. Check if the remote repo exists: `$GH_CMD repo view <username>/claude-skills 2>/dev/null`
   - If it does NOT exist, report "No claude-skills repository found on GitHub. Run /deploy-skills first to create it." and stop
2. Remove any existing temp dir: `rm -rf /tmp/claude-skills-sync`
3. Clone the repo:
   ```
   git clone https://github.com/<username>/claude-skills.git /tmp/claude-skills-sync
   ```

### Step 3: Sync skills to local

1. Check if `/tmp/claude-skills-sync/skills/` exists and has subdirectories
   - If not, report "No skills found in the repository" (but continue to check for commands)
2. For each skill directory in `/tmp/claude-skills-sync/skills/`:
   ```
   find /tmp/claude-skills-sync/skills -maxdepth 1 -mindepth 1 -type d -exec basename {} \;
   ```
3. Copy each skill to `~/.claude/skills/`, overwriting existing:
   ```
   cp -r /tmp/claude-skills-sync/skills/<skill-name> ~/.claude/skills/
   ```
   Do this for EACH skill found.

### Step 4: Sync commands to local

1. Check if `/tmp/claude-skills-sync/commands/` exists and has `.md` files
   - If not, report "No commands found in the repository" (but continue)
2. Create the target directory if needed: `mkdir -p ~/.claude/commands`
3. Copy all `.md` files:
   ```
   cp /tmp/claude-skills-sync/commands/*.md ~/.claude/commands/
   ```

### Step 5: Clean up and report results

1. Collect the list of synced skills and commands before cleanup
2. Remove the temp directory: `rm -rf /tmp/claude-skills-sync`
3. Tell the user:
   - Which skills were synced (list them)
   - Which commands were synced (list them)
   - The source repository URL: `https://github.com/<username>/claude-skills`
