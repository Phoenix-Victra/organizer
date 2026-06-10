# Session Notes — organizer

**Type:** Shell / Bash
**Repo:** https://github.com/Phoenix-Victra/organizer.git
**Last updated:** 2026-06-10

## In Progress
- Session manager is complete and working
- `phoenix.sh` — interactive TUI (wrap/pick/quit)
- `session-manager.sh` — called by Claude Code on "wrap up"

## Open TODOs
- [ ] Nothing outstanding — fully working

## Next Steps
- Type `phoenix` in Git Bash to open the screen
- Type `wrap` to save all local projects to OneDrive
- Say "wrap up" in Claude Code to save AI session notes
- Say "pick up" in Claude Code to resume a project

## Key Decisions
- OneDrive detected by scanning for whichever OneDrive* folder already contains `phoenix work`
- Remote Claude Code sessions commit SESSION_NOTES.md to the repo and push — syncs via git pull
- Local projects are rsynced into `phoenix work/<Type>/<project>/files/` by the TUI
- `set -euo pipefail` removed from phoenix.sh for Git Bash / MinTTY compatibility
- `read -n1` replaced with `read -r` + Enter prompt for MinTTY compatibility

## Setup (already done)
```bash
git clone https://github.com/Phoenix-Victra/organizer.git ~/organizer
chmod +x ~/organizer/phoenix.sh ~/organizer/session-manager.sh
echo 'alias phoenix="bash ~/organizer/phoenix.sh"' >> ~/.bashrc
source ~/.bashrc
```
