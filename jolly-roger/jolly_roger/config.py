"""Central config — all values come from environment / .env file."""

import os
from dotenv import load_dotenv

load_dotenv()

# Google
GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]
GBP_ACCOUNT_ID = os.environ["GBP_ACCOUNT_ID"]      # e.g. "accounts/123456789"
GBP_LOCATION_ID = os.environ["GBP_LOCATION_ID"]    # e.g. "locations/987654321"
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "..", "token.json")
OAUTH_SCOPES = ["https://www.googleapis.com/auth/business.manage"]

# Anthropic
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
CLAUDE_MODEL = "claude-sonnet-4-6"

# Email
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
DIGEST_TO = os.environ["DIGEST_TO"]

# Flask
FLASK_SECRET_KEY = os.environ["FLASK_SECRET_KEY"]
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "127.0.0.1")
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "5000"))

# SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "reviews.db")

# Tone guidance fed to Claude for every reply draft
REPLY_TONE = os.getenv("REPLY_TONE_NOTES", """
You are writing a reply on behalf of The Jolly Roger Restaurant and Bar, a casual seafood
restaurant and bar in Kill Devil Hills, NC on the Outer Banks. The voice is warm, genuine,
and personal — like a message from the owner or a caring manager, not corporate copy.

Guidelines:
- Thank the guest by name if available.
- Reference a specific detail from their review so it doesn't feel templated.
- For 4–5 star reviews: express genuine gratitude, invite them back.
- For 3-star reviews: acknowledge what fell short, affirm the standard, invite another visit.
- For 1–2 star reviews: lead with empathy, take responsibility (don't make excuses), offer to
  make it right (invite them to reach out directly: info@jollyrognerkdh.com). Never argue.
- Keep replies under 120 words.
- Never include personal information about the reviewer beyond their first name.
- Never use promotional language or discounts in replies.
- End with a warm sign-off like "Hope to see you again soon!" or "We'd love the chance to
  make it right — please reach out anytime."
""".strip())

# Reviews that score ≤ this get a SENSITIVE flag so the human knows to handle carefully
SENSITIVE_STAR_THRESHOLD = 2
