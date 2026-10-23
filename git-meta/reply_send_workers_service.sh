#!/bin/zsh
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_DIR="$HOME/Library/LaunchAgents"
LOG_DIR="$PROJECT_DIR/logs"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python3"
WORKER_FILE="$PROJECT_DIR/outreach_reply_send_worker.py"
DOMAIN="gui/$(id -u)"

ACCOUNT_IDS=(
  outreach_account_01
  outreach_account_02
  outreach_account_03
  outreach_account_04
  outreach_account_05
  outreach_account_06
  outreach_account_07
)

label_for() {
  local account_id="$1"
  echo "com.linkedin.daily-scanner.reply-send.${account_id//_/-}"
}

plist_for() {
  local account_id="$1"
  echo "$PLIST_DIR/$(label_for "$account_id").plist"
}

validate_project() {
  if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Missing virtualenv Python: $PYTHON_BIN" >&2
    exit 1
  fi
  if [[ ! -f "$WORKER_FILE" ]]; then
    echo "Missing reply-send worker: $WORKER_FILE" >&2
    exit 1
  fi
  if [[ ! -f "$PROJECT_DIR/.env" ]]; then
    echo "Missing environment file: $PROJECT_DIR/.env" >&2
    exit 1
  fi
}

write_plist() {
  local account_id="$1"
  local label="$(label_for "$account_id")"
  local plist_path="$(plist_for "$account_id")"

  "$PYTHON_BIN" - \
    "$plist_path" \
    "$label" \
    "$PROJECT_DIR" \
    "$PYTHON_BIN" \
    "$WORKER_FILE" \
    "$LOG_DIR" \
    "$HOME" \
    "$account_id" <<'PY'
import plistlib
import sys

(
    plist_path,
    label,
    project_dir,
    python_bin,
    worker_file,
    log_dir,
    home,
    account_id,
) = sys.argv[1:]

payload = {
    "Label": label,
    "ProgramArguments": [
        "/usr/bin/caffeinate",
        "-i",
        python_bin,
        "-u",
        worker_file,
        "--account-id",
        account_id,
    ],
    "WorkingDirectory": project_dir,
    "RunAtLoad": True,
    "KeepAlive": True,
    "ThrottleInterval": 10,
    "ProcessType": "Background",
    "EnvironmentVariables": {
        "HOME": home,
        "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "PYTHONUNBUFFERED": "1",
    },
    "StandardOutPath": f"{log_dir}/reply-send-{account_id}.out.log",
    "StandardErrorPath": f"{log_dir}/reply-send-{account_id}.err.log",
}

with open(plist_path, "wb") as output:
    plistlib.dump(payload, output)
PY

  /usr/bin/plutil -lint "$plist_path" >/dev/null
}

install_services() {
  validate_project
  mkdir -p "$PLIST_DIR" "$LOG_DIR"

  for account_id in "${ACCOUNT_IDS[@]}"; do
    local label="$(label_for "$account_id")"
    local plist_path="$(plist_for "$account_id")"
    write_plist "$account_id"
    launchctl bootout "$DOMAIN/$label" 2>/dev/null || true
    launchctl bootstrap "$DOMAIN" "$plist_path"
    launchctl enable "$DOMAIN/$label"
    launchctl kickstart -k "$DOMAIN/$label"
    echo "Started: $account_id"
  done

  echo "Reply-send workers installed for all ${#ACCOUNT_IDS[@]} Outreach accounts."
  echo "Logs: $LOG_DIR/reply-send-outreach_account_*.out.log"
}

status_services() {
  for account_id in "${ACCOUNT_IDS[@]}"; do
    local label="$(label_for "$account_id")"
    echo "[$account_id]"
    launchctl print "$DOMAIN/$label" 2>/dev/null \
      | grep -E "state =|pid =|last exit code" \
      || echo "not installed"
  done
}

uninstall_services() {
  for account_id in "${ACCOUNT_IDS[@]}"; do
    local label="$(label_for "$account_id")"
    local plist_path="$(plist_for "$account_id")"
    launchctl bootout "$DOMAIN/$label" 2>/dev/null || true
    if [[ -f "$plist_path" ]]; then
      mv "$plist_path" "$plist_path.disabled"
    fi
    echo "Stopped: $account_id"
  done
}

case "${1:-install}" in
  install)
    install_services
    ;;
  restart)
    install_services
    ;;
  status)
    status_services
    ;;
  uninstall)
    uninstall_services
    ;;
  *)
    echo "Usage: $0 [install|restart|status|uninstall]" >&2
    exit 2
    ;;
esac
