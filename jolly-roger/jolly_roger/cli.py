"""Entry points for the CLI."""

import argparse
import logging
import sys


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    parser = argparse.ArgumentParser(prog="jolly-roger", description="Jolly Roger Review Monitor")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # --- poll ---
    p_poll = sub.add_parser("poll", help="Fetch new reviews, draft replies, send digest")
    p_poll.add_argument("--dashboard-url", default="http://localhost:5000",
                        help="Base URL of the dashboard (included in digest email links)")
    p_poll.add_argument("--no-email", action="store_true", help="Skip sending the digest email")

    # --- serve ---
    p_serve = sub.add_parser("serve", help="Run the approval dashboard")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=5000)
    p_serve.add_argument("--debug", action="store_true")

    # --- auth ---
    sub.add_parser("auth", help="Run the Google OAuth flow and save token.json")

    # --- init-db ---
    sub.add_parser("init-db", help="Initialise (or migrate) the SQLite database")

    args = parser.parse_args()

    if args.cmd == "poll":
        from .poller import run
        count = run(dashboard_url=args.dashboard_url, skip_email=args.no_email)
        print(f"Done. {count} new review(s) processed.")

    elif args.cmd == "serve":
        from .dashboard import app
        app.run(host=args.host, port=args.port, debug=args.debug)

    elif args.cmd == "auth":
        from .google_auth import get_credentials
        creds = get_credentials()
        print(f"Authenticated. Token saved. Expiry: {creds.expiry}")

    elif args.cmd == "init-db":
        from .db import init_db
        init_db()
        print("Database initialised.")
