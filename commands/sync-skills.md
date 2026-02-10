---
description: Pull/sync custom skills and commands from the claude-skills GitHub repository
allowed-tools: [Bash, Read, Write, Glob, Grep]
---

# Sync Custom Skills & Commands from GitHub

Pull the latest custom skills and commands from the `claude-skills` GitHub repository into `~/.claude/skills/` and `~/.claude/commands/`.

## Instructions

Execute the following steps in order. Use Bash for all commands.

### Step 1: Check prerequisites

1. Check if `gh` CLI is installed: `command -v gh`
   - If not installed, run: `brew install gh`
   - If `brew` is also not installed, tell the user to install Homebrew first and stop
2. Check if `gh` is authenticated: `gh auth status`
   - If not authenticated, tell the user to run `gh auth login` and stop
3. Get the GitHub username: `gh api user --jq '.login'`

### Step 2: Check if git repo exists

1. Check if `~/.claude/skills/.git` exists
2. If it exists, skip to Step 4
3. If not, proceed to Step 3

### Step 3: Clone into existing directory

If `~/.claude/skills/` is not yet a git repo, initialize and connect it:

1. Check if the remote repo exists: `gh repo view <username>/claude-skills 2>/dev/null`
   - If it does NOT exist, report "No claude-skills repository found on GitHub. Run /deploy-skills first to create it." and stop
2. Initialize the repo:
   ```
   git -C ~/.claude/skills init
   git -C ~/.claude/skills branch -M main
   git -C ~/.claude/skills remote add origin https://github.com/<username>/claude-skills.git
   ```
3. Fetch from remote: `git -C ~/.claude/skills fetch origin main`
4. Reset to match remote: `git -C ~/.claude/skills reset --mixed origin/main`
5. Checkout tracked files: `git -C ~/.claude/skills checkout -- .`

### Step 4: Pull latest changes

1. Verify origin remote points to the right repo: `git -C ~/.claude/skills remote get-url origin`
   - If no remote exists, add it: `git -C ~/.claude/skills remote add origin https://github.com/<username>/claude-skills.git`
2. Fetch latest: `git -C ~/.claude/skills fetch origin main`
3. Check if there are incoming changes: `git -C ~/.claude/skills diff HEAD..origin/main --stat`
   - If no changes, report "Already up to date. No new skills or commands to sync." and stop
4. Pull changes: `git -C ~/.claude/skills pull origin main --ff-only`
   - If fast-forward fails (local divergence), report the conflict and suggest running `/deploy-skills` to push local changes first, or `git -C ~/.claude/skills reset --hard origin/main` to discard local changes

### Step 5: Copy commands to their destination

If a `commands/` directory exists in the repo, copy command files to `~/.claude/commands/`:

1. Check if `~/.claude/skills/commands/` exists
2. If it does:
   - Create the target directory if needed: `mkdir -p ~/.claude/commands`
   - Copy all `.md` files: `cp ~/.claude/skills/commands/*.md ~/.claude/commands/`

### Step 6: Report results

1. List the custom skill directories that now exist (non-symlink, non-.git, non-commands dirs):
   ```
   find ~/.claude/skills -maxdepth 1 -mindepth 1 -type d ! -type l -not -name '.git' -not -name 'commands' -exec basename {} \;
   ```
2. List the synced commands:
   ```
   ls ~/.claude/skills/commands/*.md 2>/dev/null | xargs -I{} basename {}
   ```
3. Tell the user:
   - Which skills were synced (list them)
   - Which commands were synced (list them)
   - The source repository URL: `https://github.com/<username>/claude-skills`
   - Whether new changes were pulled or everything was already up to date
