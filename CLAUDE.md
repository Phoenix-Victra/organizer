# Claude Code — Session Manager

## Session Workflow

### "wrap up" / "end session"

Run the wrap workflow:

1. Write `SESSION_NOTES.md` directly into the **current project's repo root** with real session context:
   - **In Progress**: what was actively being worked on right now
   - **Open TODOs**: unresolved tasks, failing tests, open issues
   - **Next Steps**: concrete next actions
   - **Key Decisions**: any architectural or design choices made this session
2. Commit and push `SESSION_NOTES.md` so it syncs to the user's local machine on next `git pull`.
3. Remind the user: `git pull` in Git Bash to get the notes into their local repo (which should live inside OneDrive).
4. Print a clean summary of what was filed.

### "pick up" / "resume projects"

Run the pick workflow:

1. Execute `bash /home/user/organizer/session-manager.sh pick` to find all SESSION_NOTES.md files.
2. Display a formatted summary per project: status, next steps, key decisions.
3. Ask the user which project to jump into.
4. Once chosen: open the relevant files (the ones listed under In Progress / Next Steps), read them, and remind the user exactly where they left off.

## Windows Setup (Git Bash)

Install once — run these in **Git Bash**:

```bash
# 1. Clone (or pull) this repo somewhere permanent
git clone <repo-url> ~/organizer

# 2. Make scripts executable
chmod +x ~/organizer/phoenix.sh ~/organizer/session-manager.sh

# 3. Add a shortcut to your Git Bash profile
echo 'alias phoenix="bash ~/organizer/phoenix.sh"' >> ~/.bashrc
source ~/.bashrc
```

Then just type `phoenix` in Git Bash to open the interactive screen.
Claude Code on Windows should be started from Git Bash so `$HOME` resolves correctly.

## Phoenix Work Layout

```
OneDrive/phoenix work/
  Node-JS/
    my-app/
      SESSION_NOTES.md    ← what was happening
      files/              ← full working copy of the project (rsync, no build artifacts)
  Python/
    data-pipeline/
      SESSION_NOTES.md
      files/
  organizer/              ← Claude Code projects: clone repo here so git pull = instant sync
    SESSION_NOTES.md
    (repo files via git)
```

**For Claude Code projects**: clone the repo into `OneDrive/phoenix work/<project>` so `git pull` syncs both the session notes and the working files at once.

**For local projects**: the `phoenix` TUI rsyncs files into the `files/` subfolder automatically on wrap.

## Project Type Detection

The script detects project roots by scanning for these markers:

| Marker | Type |
|---|---|
| `package.json` | Node/JS |
| `pyproject.toml` or `requirements.txt` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pom.xml` | Java/Maven |
| `build.gradle` | Java/Gradle |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| `CMakeLists.txt` | C/C++ |
| `*.csproj` | C#/.NET |

Search roots auto-detected from `$HOME` plus common Windows locations (`~/source/repos`, `~/projects`, `~/dev`, `~/code`, `~/workspace`, `~/Documents/projects`, `/c/dev`, `/c/projects`, `/d/dev`, etc.), up to 5 levels deep. Excludes `node_modules`, `.git`, `venv`, `dist`, `build`, `target`.
