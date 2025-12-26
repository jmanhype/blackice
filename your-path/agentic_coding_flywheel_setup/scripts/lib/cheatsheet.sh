#!/usr/bin/env bash
# ============================================================
# ACFS Cheatsheet - discover installed aliases/commands
# Source of truth: ~/.acfs/zsh/acfs.zshrc
# ============================================================

set -euo pipefail

ACFS_HOME="${ACFS_HOME:-$HOME/.acfs}"
ACFS_VERSION="${ACFS_VERSION:-0.1.0}"
CHEATSHEET_DELIM=$'\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ -f "$SCRIPT_DIR/../../VERSION" ]]; then
  ACFS_VERSION="$(cat "$SCRIPT_DIR/../../VERSION" 2>/dev/null || echo "$ACFS_VERSION")"
elif [[ -f "$ACFS_HOME/VERSION" ]]; then
  ACFS_VERSION="$(cat "$ACFS_HOME/VERSION" 2>/dev/null || echo "$ACFS_VERSION")"
fi

HAS_GUM=false
command -v gum &>/dev/null && HAS_GUM=true

print_help() {
  cat <<'EOF'
ACFS Cheatsheet (aliases + quick commands)

Usage:
  acfs cheatsheet [query]
  acfs cheatsheet --category <name>
  acfs cheatsheet --search <pattern>
  acfs cheatsheet --json
  acfs cheatsheet --zshrc <path>

Examples:
  acfs cheatsheet
  acfs cheatsheet git
  acfs cheatsheet "push"
  acfs cheatsheet --category Agents
  acfs cheatsheet --search docker
EOF
}

json_escape() {
  local s="${1:-}"
  s=${s//\\/\\\\}
  s=${s//\"/\\\"}
  s=${s//$'\n'/\\n}
  s=${s//$'\r'/\\r}
  s=${s//$'\t'/\\t}
  printf '%s' "$s"
}

normalize_category() {
  local raw="${1:-}"
  raw="${raw%% (*}"
  raw="${raw#--- }"
  raw="${raw% ---}"
  raw="${raw//aliases/}"
  raw="${raw//alias/}"
  raw="${raw//  / }"
  raw="${raw#"${raw%%[![:space:]]*}"}"
  raw="${raw%"${raw##*[![:space:]]}"}"

  case "${raw,,}" in
    *agent*) echo "Agents" ;;
    *git*) echo "Git" ;;
    *docker*) echo "Docker" ;;
    *directory*) echo "Directories" ;;
    bun*) echo "Bun" ;;
    *ubuntu*|*debian*|*convenience*) echo "System" ;;
    *modern*cli*) echo "Modern CLI" ;;
    *) [[ -n "$raw" ]] && echo "$raw" || echo "Misc" ;;
  esac
}

infer_category() {
  local name="${1:-}"
  local cmd="${2:-}"
  case "$name" in
    cc|cod|gmi|am) echo "Agents" ;;
    br|bl|bt) echo "Bun" ;;
    dev|proj|dots|p) echo "Directories" ;;
    g*) [[ "$cmd" == git* ]] && { echo "Git"; return 0; } ;;
    d*) [[ "$cmd" == docker* ]] && { echo "Docker"; return 0; } ;;
  esac
  echo "Misc"
}

cheatsheet_parse_zshrc() {
  local zshrc="${1:-$ACFS_HOME/zsh/acfs.zshrc}"
  [[ -f "$zshrc" ]] || return 1

  local current_category="Misc"
  local line rest
  local overall_active=true
  local -a if_parent_active=()
  local -a if_branch_taken=()

  while IFS= read -r line || [[ -n "$line" ]]; do
    # Section markers
    if [[ "$line" =~ ^#[[:space:]]*---[[:space:]]*(.+)[[:space:]]*---[[:space:]]*$ ]]; then
      current_category="$(normalize_category "${BASH_REMATCH[1]}")"
      continue
    fi
    if [[ "$line" =~ ^#[[:space:]]*===[[:space:]]*(.+)[[:space:]]*===[[:space:]]*$ ]]; then
      current_category="$(normalize_category "${BASH_REMATCH[1]}")"
      continue
    fi

    # Track simple conditional blocks used in acfs.zshrc (command -v ...; then / elif / else / fi).
    # This keeps the cheatsheet aligned with what will actually be active on the current system.
    if [[ "$line" =~ ^[[:space:]]*if[[:space:]]+command[[:space:]]+-v[[:space:]]+([[:alnum:]_.+-]+) ]]; then
      local tool="${BASH_REMATCH[1]}"
      local cond=false
      command -v "$tool" &>/dev/null && cond=true

      if_parent_active+=("$overall_active")
      if_branch_taken+=("$cond")

      if [[ "$overall_active" == "true" && "$cond" == "true" ]]; then
        overall_active=true
      else
        overall_active=false
      fi
      continue
    fi

    if [[ "${#if_parent_active[@]}" -gt 0 && "$line" =~ ^[[:space:]]*elif[[:space:]]+command[[:space:]]+-v[[:space:]]+([[:alnum:]_.+-]+) ]]; then
      local tool="${BASH_REMATCH[1]}"
      local idx=$(( ${#if_parent_active[@]} - 1 ))
      local parent_active="${if_parent_active[idx]}"
      local already_taken="${if_branch_taken[idx]}"

      if [[ "$already_taken" == "true" ]]; then
        overall_active=false
        continue
      fi

      local cond=false
      command -v "$tool" &>/dev/null && cond=true
      if_branch_taken[idx]="$cond"

      if [[ "$parent_active" == "true" && "$cond" == "true" ]]; then
        overall_active=true
      else
        overall_active=false
      fi
      continue
    fi

    if [[ "${#if_parent_active[@]}" -gt 0 && "$line" =~ ^[[:space:]]*else([[:space:]]*#.*)?$ ]]; then
      local idx=$(( ${#if_parent_active[@]} - 1 ))
      local parent_active="${if_parent_active[idx]}"
      local already_taken="${if_branch_taken[idx]}"

      if [[ "$parent_active" == "true" && "$already_taken" != "true" ]]; then
        overall_active=true
      else
        overall_active=false
      fi
      if_branch_taken[idx]=true
      continue
    fi

    if [[ "${#if_parent_active[@]}" -gt 0 && "$line" =~ ^[[:space:]]*fi([[:space:]]*#.*)?$ ]]; then
      local idx=$(( ${#if_parent_active[@]} - 1 ))
      overall_active="${if_parent_active[idx]}"
      unset 'if_parent_active[idx]'
      unset 'if_branch_taken[idx]'
      continue
    fi

    local line_active="$overall_active"
    # Handle one-line conditionals: `command -v tool ... && alias name='cmd'`
    # shellcheck disable=SC2250  # Regex pattern stored in variable for portability
    local oneliner_pattern='^[[:space:]]*command[[:space:]]+-v[[:space:]]+([[:alnum:]_.+-]+)[^#]*&&[[:space:]]*alias[[:space:]]'
    if [[ "$line" =~ $oneliner_pattern ]]; then
      local tool="${BASH_REMATCH[1]}"
      if ! command -v "$tool" &>/dev/null; then
        line_active=false
      fi
    fi
    [[ "$line_active" == "true" ]] || continue

    rest="$line"
    while [[ "$rest" == *"alias "* ]]; do
      # Move to the next alias segment.
      rest="${rest#*alias }"

      local name="${rest%%=*}"
      name="${name%%[[:space:]]*}"
      [[ -n "$name" ]] || break

      local value="${rest#*=}"
      [[ -n "$value" ]] || break

      local cmd="" remainder=""
      if [[ "$value" == \'* ]]; then
        value="${value#\'}"
        if [[ "$value" == *"'"* ]]; then
          cmd="${value%%\'*}"
          remainder="${value#*\'}"
        else
          cmd="$value"
          remainder=""
        fi
      elif [[ "$value" == \"* ]]; then
        value="${value#\"}"
        if [[ "$value" == *"\""* ]]; then
          cmd="${value%%\"*}"
          remainder="${value#*\"}"
        else
          cmd="$value"
          remainder=""
        fi
      else
        cmd="${value%%[[:space:]]*}"
        remainder="${value#"$cmd"}"
      fi

      local category="$current_category"
      [[ -z "$category" || "$category" == "Misc" ]] && category="$(infer_category "$name" "$cmd")"

      printf '%s%s%s%s%s%s%s\n' "$category" "$CHEATSHEET_DELIM" "$name" "$CHEATSHEET_DELIM" "$cmd" "$CHEATSHEET_DELIM" "alias"

      # Continue searching for more aliases in the same line.
      rest="$remainder"
    done
  done < "$zshrc"
}

cheatsheet_collect_entries() {
  local zshrc="${1:-$ACFS_HOME/zsh/acfs.zshrc}"
  local -a entries=()
  local line

  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    entries+=("$line")
  done < <(cheatsheet_parse_zshrc "$zshrc" || true)

  # De-dupe by name keeping the last definition (matches shell alias overriding behavior).
  local -A seen=()
  local -a dedup_rev=()
  local i
  for ((i=${#entries[@]}-1; i>=0; i--)); do
    IFS="$CHEATSHEET_DELIM" read -r _cat name _cmd _kind <<<"${entries[$i]}"
    if [[ -z "$name" || -n "${seen[$name]:-}" ]]; then
      continue
    fi
    seen[$name]=1
    dedup_rev+=("${entries[$i]}")
  done

  for ((i=${#dedup_rev[@]}-1; i>=0; i--)); do
    echo "${dedup_rev[$i]}"
  done
}

cheatsheet_filter_entries() {
  local category_filter="${1:-}"
  local search_filter="${2:-}"
  local zshrc="${3:-$ACFS_HOME/zsh/acfs.zshrc}"

  local line cat name cmd kind
  while IFS= read -r line; do
    IFS="$CHEATSHEET_DELIM" read -r cat name cmd kind <<<"$line"

    if [[ -n "$category_filter" ]]; then
      if [[ "${cat,,}" != "${category_filter,,}" ]]; then
        continue
      fi
    fi

    if [[ -n "$search_filter" ]]; then
      local hay="${cat} ${name} ${cmd}"
      if [[ "${hay,,}" != *"${search_filter,,}"* ]]; then
        continue
      fi
    fi

    echo "$line"
  done < <(cheatsheet_collect_entries "$zshrc")
}

cheatsheet_render_plain() {
  local category_filter="${1:-}"
  local search_filter="${2:-}"
  local zshrc="${3:-$ACFS_HOME/zsh/acfs.zshrc}"

  echo "ACFS Cheatsheet v$ACFS_VERSION"
  echo "Source: $zshrc"
  echo ""

  local current=""
  local cat name cmd kind line
  while IFS= read -r line; do
    IFS="$CHEATSHEET_DELIM" read -r cat name cmd kind <<<"$line"
    if [[ "$cat" != "$current" ]]; then
      current="$cat"
      echo "$current"
    fi
    printf '  %-8s %s\n' "$name" "$cmd"
  done < <(cheatsheet_filter_entries "$category_filter" "$search_filter" "$zshrc")
}

cheatsheet_render_gum() {
  local category_filter="${1:-}"
  local search_filter="${2:-}"
  local zshrc="${3:-$ACFS_HOME/zsh/acfs.zshrc}"

  gum style --bold --foreground "#89b4fa" "ACFS Cheatsheet v$ACFS_VERSION"
  gum style --foreground "#6c7086" "Source: $zshrc"
  echo ""

  local current=""
  local cat name cmd kind line
  while IFS= read -r line; do
    IFS="$CHEATSHEET_DELIM" read -r cat name cmd kind <<<"$line"
    if [[ "$cat" != "$current" ]]; then
      current="$cat"
      echo ""
      gum style --bold --foreground "#cba6f7" "$current"
    fi
    printf '  %-8s %s\n' "$name" "$cmd"
  done < <(cheatsheet_filter_entries "$category_filter" "$search_filter" "$zshrc")
}

cheatsheet_render_json() {
  local category_filter="${1:-}"
  local search_filter="${2:-}"
  local zshrc="${3:-$ACFS_HOME/zsh/acfs.zshrc}"

  local first=true
  printf '{'
  printf '"version":"%s",' "$(json_escape "$ACFS_VERSION")"
  printf '"source":"%s",' "$(json_escape "$zshrc")"
  printf '"entries":['

  local cat name cmd kind line
  while IFS= read -r line; do
    IFS="$CHEATSHEET_DELIM" read -r cat name cmd kind <<<"$line"
    if [[ "$first" == "true" ]]; then
      first=false
    else
      printf ','
    fi
    printf '{'
    printf '"category":"%s",' "$(json_escape "$cat")"
    printf '"name":"%s",' "$(json_escape "$name")"
    printf '"command":"%s",' "$(json_escape "$cmd")"
    printf '"kind":"%s"' "$(json_escape "$kind")"
    printf '}'
  done < <(cheatsheet_filter_entries "$category_filter" "$search_filter" "$zshrc")

  printf ']'
  printf '}\n'
}

main() {
  local zshrc="$ACFS_HOME/zsh/acfs.zshrc"
  local category_filter=""
  local search_filter=""
  local json_mode=false

  while [[ $# -gt 0 ]]; do
    case "$1" in
      --help|-h)
        print_help
        return 0
        ;;
      --json)
        json_mode=true
        shift
        ;;
      --category)
        if [[ -z "${2:-}" ]]; then
          echo "Error: --category requires a value" >&2
          return 1
        fi
        category_filter="$2"
        shift 2
        ;;
      --search)
        if [[ -z "${2:-}" ]]; then
          echo "Error: --search requires a value" >&2
          return 1
        fi
        search_filter="$2"
        shift 2
        ;;
      --zshrc)
        if [[ -z "${2:-}" ]]; then
          echo "Error: --zshrc requires a path" >&2
          return 1
        fi
        zshrc="$2"
        shift 2
        ;;
      *)
        # Treat positional arg as either category match or a search term.
        local q="$1"
        shift
        case "${q,,}" in
          agents|git|docker|directories|system|bun|modern\ cli)
            category_filter="$q"
            ;;
          *)
            search_filter="$q"
            ;;
        esac
        ;;
    esac
  done

  if [[ ! -f "$zshrc" ]]; then
    echo "Error: zshrc not found: $zshrc" >&2
    echo "Hint: re-run the ACFS installer, or pass --zshrc <path> / set ACFS_HOME." >&2
    return 1
  fi

  if [[ "$json_mode" == "true" ]]; then
    cheatsheet_render_json "$category_filter" "$search_filter" "$zshrc"
  elif [[ "$HAS_GUM" == "true" ]]; then
    cheatsheet_render_gum "$category_filter" "$search_filter" "$zshrc"
  else
    cheatsheet_render_plain "$category_filter" "$search_filter" "$zshrc"
  fi
}

main "$@"
