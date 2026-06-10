#!/usr/bin/env bash
# Session manager — auto-detects project roots by type marker and manages SESSION_NOTES.md
set -euo pipefail

MODE="${1:-}"  # "wrap" or "pick"

# Build search roots — works in Git Bash on Windows and Linux/macOS
_build_search_roots() {
  local -a roots=("${HOME}")

  # Git Bash on Windows: $HOME is /c/Users/<name>
  # Add common Windows project locations
  local win_home="${HOME}"
  local candidates=(
    "${win_home}/source"
    "${win_home}/source/repos"
    "${win_home}/repos"
    "${win_home}/projects"
    "${win_home}/dev"
    "${win_home}/code"
    "${win_home}/workspace"
    "${win_home}/Documents/projects"
    "${win_home}/Documents/repos"
    "${win_home}/Desktop"
    "/c/dev"
    "/c/projects"
    "/c/repos"
    "/d/dev"
    "/d/projects"
    "/d/repos"
  )

  for c in "${candidates[@]}"; do
    [[ -d "$c" ]] && roots+=("$c")
  done

  printf '%s\n' "${roots[@]}" | sort -u
}

SEARCH_ROOTS=()
while IFS= read -r r; do SEARCH_ROOTS+=("$r"); done < <(_build_search_roots)

# --- Type markers: maps filename -> project type label
declare -A TYPE_MARKERS=(
  ["package.json"]="Node/JS"
  ["pyproject.toml"]="Python"
  ["requirements.txt"]="Python"
  ["Cargo.toml"]="Rust"
  ["go.mod"]="Go"
  ["pom.xml"]="Java/Maven"
  ["build.gradle"]="Java/Gradle"
  ["Gemfile"]="Ruby"
  ["composer.json"]="PHP"
  ["*.csproj"]="C#/.NET"
  ["CMakeLists.txt"]="C/C++"
)

# Find unique project roots (exclude node_modules, .git internals, venv, etc.)
find_project_roots() {
  local -a roots=()
  local seen=()

  for search_root in "${SEARCH_ROOTS[@]}"; do
    [[ -d "$search_root" ]] || continue
    for marker in "${!TYPE_MARKERS[@]}"; do
      while IFS= read -r found; do
        local dir
        dir="$(dirname "$found")"
        # Skip noise directories
        echo "$dir" | grep -qE '(node_modules|\.git|venv|\.venv|__pycache__|dist|build|target)' && continue
        # Deduplicate
        local already=0
        for s in "${seen[@]:-}"; do [[ "$s" == "$dir" ]] && already=1 && break; done
        [[ $already -eq 0 ]] && seen+=("$dir") && roots+=("$dir")
      done < <(find "$search_root" -maxdepth 5 -name "$marker" 2>/dev/null)
    done
  done

  printf '%s\n' "${roots[@]:-}" | sort -u
}

# Detect type label for a project root
detect_type() {
  local dir="$1"
  for marker in "${!TYPE_MARKERS[@]}"; do
    # shellcheck disable=SC2086
    ls "$dir"/$marker 2>/dev/null | grep -q . && echo "${TYPE_MARKERS[$marker]}" && return
  done
  echo "Unknown"
}

# ── WRAP UP ──────────────────────────────────────────────────────────────────
do_wrap() {
  local timestamp
  timestamp="$(date '+%Y-%m-%d %H:%M')"
  local -a filed=()

  while IFS= read -r root; do
    [[ -z "$root" ]] && continue
    local type
    type="$(detect_type "$root")"
    local notes_file="${root}/SESSION_NOTES.md"
    local project_name
    project_name="$(basename "$root")"

    # Build or update the notes file
    cat > "$notes_file" <<NOTES
# Session Notes — ${project_name}

**Type:** ${type}
**Last updated:** ${timestamp}

## In Progress
<!-- Fill in: what was actively being worked on -->
- (auto-detected from session context — update manually)

## Open TODOs
<!-- Fill in: unresolved tasks or issues -->
- [ ] (review open issues / uncommitted changes)

## Next Steps
<!-- Fill in: what to tackle next -->
- (continue from last known state)

## Key Decisions
<!-- Fill in: architectural or design choices made -->
- (none recorded yet)

## Git Status
$(cd "$root" && git status --short 2>/dev/null || echo "Not a git repo")

## Recent Commits
$(cd "$root" && git log --oneline -5 2>/dev/null || echo "No commits")
NOTES

    filed+=("${project_name} [${type}] → ${notes_file}")
  done < <(find_project_roots)

  echo ""
  echo "── Session wrapped at ${timestamp} ──"
  echo ""
  if [[ ${#filed[@]} -eq 0 ]]; then
    echo "No projects detected."
  else
    echo "Filed SESSION_NOTES.md for:"
    for entry in "${filed[@]}"; do
      echo "  • ${entry}"
    done
  fi
}

# ── PICK UP ──────────────────────────────────────────────────────────────────
do_pick() {
  local -a found=()

  for search_root in "${SEARCH_ROOTS[@]}"; do
    [[ -d "$search_root" ]] || continue
    while IFS= read -r notes_file; do
      found+=("$notes_file")
    done < <(find "$search_root" -maxdepth 6 -name "SESSION_NOTES.md" \
               ! -path "*/node_modules/*" ! -path "*/.git/*" 2>/dev/null | sort)
  done

  if [[ ${#found[@]} -eq 0 ]]; then
    echo "No SESSION_NOTES.md files found."
    exit 0
  fi

  echo ""
  echo "── Projects with saved session notes ──"
  echo ""

  for notes_file in "${found[@]}"; do
    local project_name
    project_name="$(basename "$(dirname "$notes_file")")"
    echo "▸ ${project_name}  (${notes_file})"
    echo "---"
    cat "$notes_file"
    echo ""
  done
}

case "$MODE" in
  wrap)  do_wrap ;;
  pick)  do_pick ;;
  *)
    echo "Usage: $0 <wrap|pick>"
    echo "  wrap  — scan projects, create/update SESSION_NOTES.md in each"
    echo "  pick  — find all SESSION_NOTES.md and print a summary"
    exit 1
    ;;
esac
