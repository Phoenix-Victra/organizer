# Claude Code — Session Manager

## Session Workflow

### "wrap up" / "end session"

Run the wrap workflow:

1. Execute `bash /home/user/organizer/session-manager.sh wrap` to auto-detect all projects and scaffold SESSION_NOTES.md in each root.
2. For **each detected project**, enrich its SESSION_NOTES.md with real context from the current session:
   - **In Progress**: what was actively being worked on right now
   - **Open TODOs**: unresolved tasks, failing tests, open issues
   - **Next Steps**: concrete next actions
   - **Key Decisions**: any architectural or design choices made this session
3. Print a clean summary of every project filed away.

### "pick up" / "resume projects"

Run the pick workflow:

1. Execute `bash /home/user/organizer/session-manager.sh pick` to find all SESSION_NOTES.md files.
2. Display a formatted summary per project: status, next steps, key decisions.
3. Ask the user which project to jump into.
4. Once chosen: open the relevant files (the ones listed under In Progress / Next Steps), read them, and remind the user exactly where they left off.

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

Search roots: `$HOME` and `/home/user`, up to 5 levels deep. Excludes `node_modules`, `.git`, `venv`, `dist`, `build`, `target`.
