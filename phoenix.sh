#!/usr/bin/env bash
# Phoenix Work — interactive session manager TUI
# Compatible with Git Bash on Windows (MinTTY)

# Find the OneDrive folder that already contains "phoenix work"
_find_onedrive() {
  for d in "${HOME}"/OneDrive*; do
    [[ -d "${d}/phoenix work" ]] && echo "$d" && return
  done
  # Fallback: first OneDrive found
  for d in "${HOME}"/OneDrive*; do
    [[ -d "$d" ]] && echo "$d" && return
  done
  echo "${HOME}"
}

_ONEDRIVE="$(_find_onedrive)"
PHOENIX_DIR="${_ONEDRIVE}/phoenix work"

# ── Type markers ─────────────────────────────────────────────────────────────
declare -A TYPE_MARKERS=(
  ["package.json"]="Node-JS"
  ["pyproject.toml"]="Python"
  ["requirements.txt"]="Python"
  ["Cargo.toml"]="Rust"
  ["go.mod"]="Go"
  ["pom.xml"]="Java"
  ["build.gradle"]="Java"
  ["Gemfile"]="Ruby"
  ["composer.json"]="PHP"
  ["CMakeLists.txt"]="C-Cpp"
)

# ── Search roots (Git Bash on Windows + Linux) ────────────────────────────────
_build_search_roots() {
  local -a roots=("${HOME}")
  local candidates=(
    "${HOME}/source" "${HOME}/source/repos"
    "${HOME}/repos"  "${HOME}/projects"
    "${HOME}/dev"    "${HOME}/code"
    "${HOME}/workspace"
    "${HOME}/Documents/projects" "${HOME}/Documents/repos"
    "${HOME}/Desktop"
    "/c/dev" "/c/projects" "/c/repos"
    "/d/dev" "/d/projects" "/d/repos"
  )
  for c in "${candidates[@]}"; do [[ -d "$c" ]] && roots+=("$c"); done
  printf '%s\n' "${roots[@]}" | sort -u
}

SEARCH_ROOTS=()
while IFS= read -r r; do SEARCH_ROOTS+=("$r"); done < <(_build_search_roots)

# ── Helpers ───────────────────────────────────────────────────────────────────
detect_type() {
  local dir="$1"
  for marker in "${!TYPE_MARKERS[@]}"; do
    [[ -f "${dir}/${marker}" ]] && echo "${TYPE_MARKERS[$marker]}" && return
  done
  ls "${dir}"/*.csproj 2>/dev/null | grep -q . && echo "CSharp" && return
  echo "Other"
}

find_project_roots() {
  local -a seen=()
  for search_root in "${SEARCH_ROOTS[@]}"; do
    [[ -d "$search_root" ]] || continue
    for marker in "${!TYPE_MARKERS[@]}"; do
      while IFS= read -r found; do
        local dir; dir="$(dirname "$found")"
        echo "$dir" | grep -qE '(node_modules|\.git|venv|\.venv|__pycache__|/dist|/build|/target)' && continue
        local already=0
        for s in "${seen[@]:-}"; do [[ "$s" == "$dir" ]] && already=1 && break; done
        [[ $already -eq 0 ]] && seen+=("$dir") && echo "$dir"
      done < <(find "$search_root" -maxdepth 5 -name "$marker" 2>/dev/null)
    done
    while IFS= read -r found; do
      local dir; dir="$(dirname "$found")"
      local already=0
      for s in "${seen[@]:-}"; do [[ "$s" == "$dir" ]] && already=1 && break; done
      [[ $already -eq 0 ]] && seen+=("$dir") && echo "$dir"
    done < <(find "$search_root" -maxdepth 5 -name "*.csproj" 2>/dev/null)
  done
}

clear_screen() { clear 2>/dev/null || printf '\033[2J\033[H'; }

pause() {
  echo ""
  printf "  Press Enter to continue..."
  read -r
}

# ── WRAP ──────────────────────────────────────────────────────────────────────
do_wrap() {
  local timestamp; timestamp="$(date '+%Y-%m-%d %H:%M')"
  local -a filed=()

  while IFS= read -r root; do
    [[ -z "$root" ]] && continue
    local type; type="$(detect_type "$root")"
    local project_name; project_name="$(basename "$root")"
    local save_dir="${PHOENIX_DIR}/${type}/${project_name}"
    mkdir -p "$save_dir"

    local git_status; git_status="$(cd "$root" && git status --short 2>/dev/null || echo 'Not a git repo')"
    local git_log;    git_log="$(cd "$root"    && git log --oneline -5 2>/dev/null || echo 'No commits')"

    cat > "${save_dir}/SESSION_NOTES.md" <<NOTES
# Session Notes — ${project_name}

**Type:** ${type}
**Source path:** ${root}
**Last updated:** ${timestamp}

## In Progress
- (fill in from session context)

## Open TODOs
- [ ] (review open issues / uncommitted changes)

## Next Steps
- (continue from last known state)

## Key Decisions
- (none recorded yet)

## Git Status
${git_status}

## Recent Commits
${git_log}
NOTES

    # Copy project files into a files/ subfolder, excluding build artifacts
    local files_dir="${save_dir}/files"
    mkdir -p "$files_dir"
    if command -v rsync &>/dev/null; then
      rsync -a --delete \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='venv' --exclude='.venv' \
        --exclude='__pycache__' \
        --exclude='dist' --exclude='build' --exclude='target' \
        --exclude='*.log' --exclude='*.tmp' \
        "${root}/" "${files_dir}/"
    else
      # fallback: plain copy without rsync
      cp -r "${root}/." "${files_dir}/" 2>/dev/null || true
      # remove noise folders if cp was used
      rm -rf "${files_dir}/node_modules" "${files_dir}/.git" \
             "${files_dir}/venv" "${files_dir}/__pycache__" \
             "${files_dir}/dist" "${files_dir}/build" "${files_dir}/target" 2>/dev/null || true
    fi

    filed+=("${type}/${project_name}")
  done < <(find_project_roots | sort)

  echo ""
  echo "  Session wrapped at ${timestamp}"
  echo "  Saved to: ${PHOENIX_DIR}"
  echo ""
  if [[ ${#filed[@]} -eq 0 ]]; then
    echo "  No projects detected."
  else
    echo "  Projects saved:"
    for entry in "${filed[@]}"; do
      echo "    + ${entry}"
    done
  fi
}

# ── CLOSE ALL WINDOWS ─────────────────────────────────────────────────────────
do_close_windows() {
  echo ""
  echo "  Closing open windows gracefully..."

  # Step 1: Close File Explorer windows via COM (graceful, no data loss)
  powershell.exe -NoProfile -Command \
    "(New-Object -ComObject Shell.Application).Windows() | ForEach-Object { \$_.Quit() }" \
    2>/dev/null || true

  # Step 2: Send graceful close signal to all common apps (like clicking X)
  # CloseMainWindow() triggers save dialogs — no data gets lost
  powershell.exe -NoProfile -Command "
    \$apps = @(
      'Code','Cursor','notepad','Notepad++',
      'chrome','msedge','firefox','opera',
      'slack','Teams','Discord',
      'OUTLOOK','WINWORD','EXCEL','POWERPNT',
      'WindowsTerminal','wt'
    )
    foreach (\$name in \$apps) {
      Get-Process \$name -ErrorAction SilentlyContinue |
        ForEach-Object { \$_.CloseMainWindow() | Out-Null }
    }
  " 2>/dev/null || true

  # Step 3: Wait for apps to finish saving and close on their own
  echo "  Waiting for apps to finish saving..."
  sleep 4

  # Step 4: Force close anything still running
  powershell.exe -NoProfile -Command "
    \$apps = @(
      'Code','Cursor','notepad','Notepad++',
      'chrome','msedge','firefox','opera',
      'slack','Teams','Discord',
      'OUTLOOK','WINWORD','EXCEL','POWERPNT',
      'WindowsTerminal','wt'
    )
    foreach (\$name in \$apps) {
      Get-Process \$name -ErrorAction SilentlyContinue | Stop-Process -Force
    }
  " 2>/dev/null || true

  # Step 5: Close other Git Bash / mintty windows (not this one)
  powershell.exe -NoProfile -Command "
    Get-Process mintty,bash -ErrorAction SilentlyContinue |
      Where-Object { \$_.Id -ne $PPID -and \$_.Id -ne $$ } |
      ForEach-Object { \$_.CloseMainWindow() | Out-Null }
  " 2>/dev/null || true

  sleep 1

  echo "  All windows closed."
}

# ── PICK ──────────────────────────────────────────────────────────────────────
do_pick() {
  local -a notes_files=()
  while IFS= read -r f; do notes_files+=("$f"); done \
    < <(find "${PHOENIX_DIR}" -name "SESSION_NOTES.md" 2>/dev/null | sort)

  if [[ ${#notes_files[@]} -eq 0 ]]; then
    echo ""
    echo "  No saved sessions found in ${PHOENIX_DIR}"
    echo "  Run 'wrap' first to save your projects."
    return
  fi

  echo ""
  echo "  -- Saved Projects ----------------------------------"
  echo ""

  for f in "${notes_files[@]}"; do
    local rel; rel="${f#${PHOENIX_DIR}/}"
    local category; category="$(echo "$rel" | cut -d/ -f1)"
    local project;  project="$(echo "$rel"  | cut -d/ -f2)"
    echo "  [${category}] ${project}"

    local in_next=0
    while IFS= read -r line; do
      [[ "$line" == "## Next Steps" ]] && in_next=1 && continue
      [[ "$line" == "## "* ]] && in_next=0
      [[ $in_next -eq 1 && -n "$line" ]] && echo "      -> ${line}"
    done < "$f"
    echo ""
  done
  echo "  ----------------------------------------------------"
}

# ── TUI LOOP ──────────────────────────────────────────────────────────────────
main() {
  mkdir -p "${PHOENIX_DIR}"

  while true; do
    clear_screen
    echo ""
    echo "  +-------------------------------+"
    echo "  |    Phoenix Work Manager       |"
    echo "  +-------------------------------+"
    echo ""
    echo "  Saving to: ${PHOENIX_DIR}"
    echo ""
    echo "    wrap   -- save all projects and close"
    echo "    pick   -- browse saved sessions"
    echo "    quit   -- exit without saving"
    echo ""
    printf "  > "
    read -r cmd

    # lowercase
    cmd="$(echo "$cmd" | tr '[:upper:]' '[:lower:]' | xargs)"

    case "$cmd" in
      wrap|"end session"|"wrap up")
        clear_screen
        echo ""
        echo "  Scanning projects..."
        echo ""
        do_wrap
        do_close_windows
        echo ""
        echo "  All done. Closing this window..."
        sleep 2
        exit 0
        ;;
      pick|"pick up"|resume|"resume projects")
        clear_screen
        do_pick
        pause
        ;;
      quit|exit|q)
        clear_screen
        break
        ;;
      *)
        clear_screen
        echo ""
        echo "  Unknown: '${cmd}'"
        echo "  Commands: wrap  pick  quit"
        sleep 1
        ;;
    esac
  done
}

main
