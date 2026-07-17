#!/usr/bin/env bash
# EC2 agent/runtime dashboard. Ref: codex/tasks/104-agent-task-monitoring.md

set -uo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
SCRIPT_PATH="${BASH_SOURCE[0]}"

if [[ "${1:-}" == "--watch" ]]; then
    if ! command -v watch >/dev/null 2>&1; then
        printf 'error: watch is not installed\n' >&2
        exit 1
    fi
    exec env FORCE_COLOR=1 watch --color --interval 10 "bash $SCRIPT_PATH"
elif [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    printf 'Usage: %s [--watch]\n' "$0"
    printf '  --watch  Refresh the dashboard every 10 seconds with watch(1).\n'
    exit 0
elif [[ $# -gt 0 ]]; then
    printf 'error: unknown argument: %s\n' "$1" >&2
    printf 'Usage: %s [--watch]\n' "$0" >&2
    exit 2
fi

if [[ ! -d "$REPO_ROOT/codex/tasks" ]]; then
    REPO_ROOT="/home/ubuntu/Affiliate-Ai"
fi
MONITOR_TASKS_PATH="$SCRIPT_DIR/monitor_tasks.py"
if [[ ! -f "$MONITOR_TASKS_PATH" ]]; then
    MONITOR_TASKS_PATH="$REPO_ROOT/scripts/dev/monitor_tasks.py"
fi

if [[ -z "${NO_COLOR:-}" && ( -n "${FORCE_COLOR:-}" || -t 1 ) ]]; then
    RESET=$'\033[0m'
    BOLD=$'\033[1m'
    DIM=$'\033[2m'
    RED=$'\033[31m'
    GREEN=$'\033[32m'
    YELLOW=$'\033[33m'
    BLUE=$'\033[34m'
    CYAN=$'\033[36m'
    WHITE=$'\033[37m'
else
    RESET=''
    BOLD=''
    DIM=''
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    CYAN=''
    WHITE=''
fi

section() {
    printf '\n%s%s== %s ==%s\n' "$BOLD" "$BLUE" "$1" "$RESET"
}

command_summary() {
    local process_name="$1"
    local command_line="$2"
    local word base
    local -a words summary_words
    local found=0

    read -r -a words <<< "$command_line"
    summary_words=("$process_name")

    for word in "${words[@]}"; do
        base="${word##*/}"
        if (( found == 0 )); then
            if [[ "$base" == "$process_name" ]]; then
                found=1
            fi
            continue
        fi

        case "$word" in
            -p|-q|--prompt|--prompt=*)
                summary_words+=("$word" "<input>")
                break
                ;;
            --api-key|--token|--secret|--password)
                summary_words+=("$word" "<redacted>")
                break
                ;;
            --api-key=*|--token=*|--secret=*|--password=*)
                summary_words+=("${word%%=*}=<redacted>")
                ;;
            --*=*)
                summary_words+=("${word%%=*}=<value>")
                ;;
            -*)
                summary_words+=("$word")
                ;;
            exec|resume|review|run|status)
                if (( ${#summary_words[@]} == 1 )); then
                    summary_words+=("$word")
                else
                    summary_words+=("<input>")
                    break
                fi
                ;;
            *)
                summary_words+=("<input>")
                break
                ;;
        esac

        if (( ${#summary_words[@]} >= 7 )); then
            summary_words+=("...")
            break
        fi
    done

    printf '%s' "${summary_words[*]}"
}

agent_is_running() {
    local process_name command_line

    while read -r process_name command_line; do
        case "$process_name" in
            codex|claude|agy) ;;
            *) continue ;;
        esac
        case "$command_line" in
            *app-server*|*stream-json*|*code_mode_host*|*input-format*) continue ;;
        esac
        return 0
    done < <(ps -eo comm=,args= 2>/dev/null)

    return 1
}

show_agent_processes() {
    local pid runtime process_name command_line task argument quoted_task
    local index exec_index
    local -a process_args
    local found=0

    printf '%s%s%-8s %-12s %-10s %s%s\n' \
        "$BOLD" "$WHITE" 'PID' 'RUNTIME' 'AGENT' 'CURRENT TASK' "$RESET"
    while read -r pid runtime process_name command_line; do
        case "$process_name" in
            codex|claude|agy) ;;
            *) continue ;;
        esac
        # Skip IDE background servers (not actual task execution)
        case "$command_line" in
            *app-server*|*stream-json*|*code_mode_host*|*input-format*) continue ;;
        esac
        found=1

        process_args=()
        if [[ -r "/proc/$pid/cmdline" ]]; then
            while IFS= read -r -d '' argument; do
                process_args+=("$argument")
            done < "/proc/$pid/cmdline"
        fi

        task=''
        case "$process_name" in
            codex)
                exec_index=-1
                for (( index = 0; index < ${#process_args[@]}; index++ )); do
                    if [[ "${process_args[index]}" == 'exec' ]]; then
                        exec_index=$index
                    elif (( exec_index >= 0 )) && [[ "${process_args[index]}" == '--json' ]] \
                        && (( index + 1 < ${#process_args[@]} )); then
                        task="${process_args[index + 1]}"
                        break
                    fi
                done

                if [[ -z "$task" ]] && (( exec_index >= 0 && ${#process_args[@]} > exec_index + 1 )); then
                    task="${process_args[${#process_args[@]} - 1]}"
                    [[ "$task" == -* ]] && task=''
                fi

                if [[ -z "$task" && "$command_line" == *' exec '* ]]; then
                    if [[ "$command_line" == *' --json '* ]]; then
                        task="${command_line#* --json }"
                    else
                        quoted_task="$(sed -n "s/.*'\\([^']*\\)'.*/\\1/p" <<< "$command_line")"
                        task="$quoted_task"
                    fi
                fi
                ;;
            claude)
                for (( index = 0; index < ${#process_args[@]}; index++ )); do
                    if [[ "${process_args[index]}" == '-p' ]] \
                        && (( index + 1 < ${#process_args[@]} )); then
                        task="${process_args[index + 1]}"
                        break
                    fi
                done

                if [[ -z "$task" && "$command_line" == *' -p '* ]]; then
                    task="${command_line#* -p }"
                fi
                ;;
        esac

        if [[ "$task" == \'* ]]; then
            task="${task#\'}"
            task="${task%%\'*}"
        fi
        task="${task//$'\n'/ }"
        task="${task//$'\r'/ }"
        task="${task//$'\t'/ }"
        task="${task:0:100}"
        [[ -n "$task" ]] || task='(task prompt not found)'

        printf '%-8s %-12s %s%-10s%s %s\n' \
            "$pid" "$runtime" "$CYAN" "$process_name" "$RESET" "$task"
    done < <(ps -eo pid=,etime=,comm=,args= 2>/dev/null)

    if (( found == 0 )); then
        printf '%sNo codex, claude, or agy processes are running.%s\n' "$DIM" "$RESET"
    fi
}

show_tmux_sessions() {
    local output
    if ! command -v tmux >/dev/null 2>&1; then
        printf '%stmux is not installed.%s\n' "$YELLOW" "$RESET"
        return
    fi

    if output="$(tmux list-sessions -F $'#{session_name}\t#{session_windows} windows\tcreated #{t:session_created}\t#{?session_attached,attached,detached}' 2>/dev/null)"; then
        printf '%s\n' "$output"
    else
        printf '%sNo active tmux sessions.%s\n' "$DIM" "$RESET"
    fi
}

show_recent_commits() {
    local hash commit_date author subject
    local found=0

    if ! git -C "$REPO_ROOT" rev-parse --git-dir >/dev/null 2>&1; then
        printf '%sRepository metadata is unavailable.%s\n' "$RED" "$RESET"
        return
    fi

    while IFS=$'\t' read -r hash commit_date author subject; do
        [[ -n "$hash" ]] || continue
        found=1
        printf '%s%s%s %s%s%s %s%s%s %s— %s%s\n' \
            "$YELLOW" "$hash" "$RESET" \
            "$DIM" "$commit_date" "$RESET" \
            "$CYAN" "$author" "$RESET" \
            "$WHITE" "$subject" "$RESET"
    done < <(git -C "$REPO_ROOT" log -5 --date=short --pretty=tformat:'%h%x09%ad%x09%an%x09%s' 2>/dev/null)

    if (( found == 0 )); then
        printf '%sNo commits found.%s\n' "$DIM" "$RESET"
    fi
}

show_recent_files() {
    local epoch timestamp filename
    local found=0

    while IFS=$'\t' read -r epoch timestamp filename; do
        [[ -n "$filename" ]] || continue
        found=1
        printf '%s%s%s %s%s%s\n' \
            "$DIM" "$timestamp" "$RESET" "$GREEN" "$filename" "$RESET"
    done < <({
        cd "$REPO_ROOT" || exit 1
        find scripts tests -type f -mmin -10 \
            ! -path '*/__pycache__/*' ! -name '*.pyc' \
            -printf '%T@\t%TY-%Tm-%Td %TH:%TM:%TS\t%p\n' 2>/dev/null
    } | sort -t $'\t' -k1,1nr)

    if (( found == 0 )); then
        printf '%sNo files changed in scripts/ or tests/ during the last 10 minutes.%s\n' "$DIM" "$RESET"
    fi
}

show_scraper_result() {
    local scraped_dir="$REPO_ROOT/.cache/shopee/scraped"
    local latest

    if [[ ! -d "$scraped_dir" ]]; then
        printf '%sNo scraper output directory found.%s\n' "$DIM" "$RESET"
        return
    fi

    latest="$(find "$scraped_dir" -maxdepth 1 -type f -name '*.json' \
        -printf '%T@\t%p\n' 2>/dev/null | sort -t $'\t' -k1,1nr | head -n 1 | cut -f2-)"
    if [[ -z "$latest" ]]; then
        printf '%sNo scraper result files found.%s\n' "$DIM" "$RESET"
        return
    fi

    python3 - "$latest" "$RED" "$GREEN" "$RESET" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
red, green, reset = sys.argv[2:5]
try:
    payload = json.loads(path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    raise SystemExit(0)

niches = payload.get("niches", {})
counts = {
    str(name): len(products)
    for name, products in niches.items()
    if isinstance(products, list)
} if isinstance(niches, dict) else {}
print(f"Scraped at: {payload.get('scraped_at', 'unknown')}")
if counts:
    values = []
    for name, count in sorted(counts.items()):
        color = green if count > 0 else red
        values.append(f"{color}{name}={count}{reset}")
    print("Niches: " + ", ".join(values))
PY
}

show_warp_status() {
    local status_output mode_line port listener

    if command -v warp-cli >/dev/null 2>&1; then
        status_output="$(timeout 5 warp-cli --accept-tos status 2>&1)"
        if [[ -n "$status_output" ]]; then
            status_output="${status_output//Disconnected/${RED}Disconnected${RESET}}"
            status_output="${status_output//Connected/${GREEN}Connected${RESET}}"
            printf '%s\n' "$status_output"
        else
            printf '%sWARP status returned no output.%s\n' "$YELLOW" "$RESET"
        fi

        mode_line="$(timeout 5 warp-cli --accept-tos settings 2>/dev/null | sed -n '/Mode:/p' | head -n 1)"
        if [[ -n "$mode_line" ]]; then
            printf '%s\n' "$mode_line"
            port="$(sed -n 's/.*port \([0-9][0-9]*\).*/\1/p' <<< "$mode_line")"
            if [[ -n "$port" ]] && command -v ss >/dev/null 2>&1; then
                listener="$(ss -ltn 2>/dev/null | awk -v suffix=":$port" '$4 ~ suffix "$" {print; exit}')"
                if [[ -n "$listener" ]]; then
                    printf '%sProxy listener: active on port %s%s\n' "$GREEN" "$port" "$RESET"
                else
                    printf '%sProxy listener: not detected on port %s%s\n' "$YELLOW" "$port" "$RESET"
                fi
            fi
        fi
    elif command -v systemctl >/dev/null 2>&1; then
        printf 'warp-svc service: %s\n' "$(systemctl is-active warp-svc.service 2>/dev/null || true)"
        printf '%swarp-cli is not installed; proxy mode cannot be inspected.%s\n' "$YELLOW" "$RESET"
    else
        printf '%sWARP tooling is unavailable.%s\n' "$YELLOW" "$RESET"
    fi
}

show_resources() {
    printf '%sDisk (/):%s\n' "$BOLD" "$RESET"
    df -hP / 2>/dev/null | awk 'NR == 1 || NR == 2 {print}'
    printf '%sMemory:%s\n' "$BOLD" "$RESET"
    if command -v free >/dev/null 2>&1; then
        free -h | awk 'NR == 1 || /^Mem:/ || /^Swap:/ {print}'
    else
        awk '/MemTotal|MemAvailable|SwapTotal|SwapFree/ {print}' /proc/meminfo
    fi
}

if agent_is_running; then
    STATUS_DOT_COLOR="$GREEN"
else
    STATUS_DOT_COLOR="$DIM"
fi

printf '%s●%s %s%sAffiliate AI - EC2 Agent Monitor%s\n' \
    "$STATUS_DOT_COLOR" "$RESET" "$BOLD" "$CYAN" "$RESET"
printf '%sUpdated: %s | Host: %s | Branch: %s%s\n' "$DIM" \
    "$(date --iso-8601=seconds)" "$(hostname)" \
    "$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null || printf 'unknown')" "$RESET"

section 'AI Agent Processes'
show_agent_processes

section 'Task Status'
if [[ -x "$MONITOR_TASKS_PATH" ]]; then
    "$MONITOR_TASKS_PATH" --repo-root "$REPO_ROOT" --active-only
else
    python3 "$MONITOR_TASKS_PATH" --repo-root "$REPO_ROOT" --active-only
fi

section 'tmux Sessions'
show_tmux_sessions

section 'Recent Git Commits (Last 5)'
show_recent_commits

section 'Recently Modified Files (Last 10 Minutes)'
show_recent_files

section 'Last Shopee Scraper Run'
show_scraper_result

section 'Cloudflare WARP Proxy'
show_warp_status

section 'Disk and Memory'
show_resources
