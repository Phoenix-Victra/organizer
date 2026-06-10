# Session Notes — organizer

**Type:** Shell / Bash
**Repo:** phoenix-victra/organizer
**Last updated:** 2026-06-10

## In Progress
- Building a session manager for Claude Code + Windows Git Bash
- Two entry points: `phoenix.sh` (interactive TUI) and `session-manager.sh` (called by Claude on "wrap up")

## Open TODOs
- [ ] Clone the repo locally on Windows into a folder inside OneDrive so `git pull` syncs SESSION_NOTES.md automatically
- [ ] Run `chmod +x ~/organizer/phoenix.sh ~/organizer/session-manager.sh` after cloning
- [ ] Add `alias phoenix="bash ~/organizer/phoenix.sh"` to `~/.bashrc`
- [ ] Test `phoenix` TUI on Windows Git Bash — previous bug (silent exit) was fixed in last commit

## Next Steps
1. Clone repo on Windows into `OneDrive/phoenix work/organizer` (or anywhere inside OneDrive)
2. Run `git pull` after any Claude Code session to get fresh SESSION_NOTES.md
3. Use `phoenix` TUI for local project scanning and pick-up
4. Use Claude Code "wrap up" for AI-session notes — they push here and sync via git

## Key Decisions
- **Remote sessions can't write to OneDrive directly** — SESSION_NOTES.md is committed to the repo and syncs via `git pull`
- **Local projects** (non-git) are handled by the `phoenix` TUI which writes directly to `OneDrive/phoenix work/<Type>/<project>/`
- **Two save paths, one place**: clone this repo inside OneDrive so both flows land in the same folder
- Dropped `set -euo pipefail` from phoenix.sh — it caused silent exits in Git Bash/MinTTY
- `read -n1` replaced with `read -r` + Enter prompt for MinTTY compatibility
- Save folder name uses a space (`phoenix work`) to match the user's existing File Explorer folder
