#!/usr/bin/env bash
# Wrapper for cron — activate venv and run the poller.
# Add to crontab with: crontab -e
#   0 8,14,20 * * * /path/to/jolly-roger/cron_poll.sh >> /var/log/jolly-roger.log 2>&1

set -euo pipefail
cd "$(dirname "$0")"

source .venv/bin/activate
jolly-roger poll --dashboard-url "${DASHBOARD_URL:-http://localhost:5000}"
