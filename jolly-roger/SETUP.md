# Jolly Roger — Setup Guide

## Prerequisites

- Python 3.11+
- A Google Cloud project with the **Google Business Profile APIs** enabled
- Your dad has added your Google account as **Manager or Owner** on the Business Profile
- Google has approved your [Business Profile API access request](https://developers.google.com/my-business/content/prereqs)
- An Anthropic API key from [console.anthropic.com](https://console.anthropic.com)

---

## Step 1 — Google Cloud Setup (do this first, it takes days to get approved)

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → create a new project (e.g. "Jolly Roger Reviews").
2. Enable these APIs on the project:
   - **My Business Business Information API**
   - **My Business Account Management API**
   - **My Business Verifications API**
3. Create **OAuth 2.0 credentials** (type: Desktop App). Download the JSON — you'll pull `client_id` and `client_secret` from it.
4. Submit the [Business Profile API access request form](https://developers.google.com/my-business/content/prereqs). Attach the Google Cloud project. You need approval before review listing/replies work in production.

---

## Step 2 — Install

```bash
git clone <repo-url> jolly-roger
cd jolly-roger

python3 -m venv .venv
source .venv/bin/activate      # Windows Git Bash: source .venv/Scripts/activate

pip install -e .
```

---

## Step 3 — Configure

```bash
cp .env.example .env
```

Edit `.env` and fill in every value. Key ones:

| Variable | Where to get it |
|---|---|
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | OAuth JSON from Cloud Console |
| `GBP_ACCOUNT_ID` | `accounts/<id>` — read via API once access granted |
| `GBP_LOCATION_ID` | `locations/<id>` — read via API once access granted |
| `ANTHROPIC_API_KEY` | console.anthropic.com |
| `SMTP_USER` / `SMTP_PASS` | Gmail App Password (enable 2FA, generate under Security) |
| `DIGEST_TO` | Email that receives the daily digest |
| `FLASK_SECRET_KEY` | Run: `python -c "import secrets; print(secrets.token_hex(32))"` |

---

## Step 4 — Find your Account ID and Location ID

Once GBP API access is granted, run:

```python
# find_ids.py
from jolly_roger.google_auth import get_credentials
import requests

creds = get_credentials()
headers = {"Authorization": f"Bearer {creds.token}"}

# List accounts
r = requests.get("https://mybusinessaccountmanagement.googleapis.com/v1/accounts", headers=headers)
print("Accounts:", r.json())

# List locations for first account
account_id = r.json()["accounts"][0]["name"]  # e.g. "accounts/123456789"
r2 = requests.get(f"https://mybusinessbusinessinformation.googleapis.com/v1/{account_id}/locations", headers=headers)
print("Locations:", r2.json())
```

Set `GBP_ACCOUNT_ID` and `GBP_LOCATION_ID` in `.env` with what you find.

---

## Step 5 — Authenticate with Google

```bash
jolly-roger auth
```

A browser window opens → sign in with the account your dad granted Manager access to → approve. `token.json` is created (gitignored).

---

## Step 6 — Test the poller (dry run, no email)

```bash
jolly-roger init-db
jolly-roger poll --no-email
```

Check that reviews appear without errors.

---

## Step 7 — Run the dashboard

```bash
jolly-roger serve
```

Open [http://localhost:5000](http://localhost:5000). You should see fetched reviews. Click into a drafted review → edit the reply → Approve & Post.

---

## Step 8 — Schedule the poller (cron)

The server must be always-on (VPS, Raspberry Pi, cloud VM — not a laptop):

```bash
chmod +x cron_poll.sh
crontab -e
```

Add (polls at 8am, 2pm, 8pm):

```
0 8,14,20 * * * /absolute/path/to/jolly-roger/cron_poll.sh >> /var/log/jolly-roger.log 2>&1
```

Run the dashboard as a service (e.g. systemd or `screen`):

```bash
jolly-roger serve --host 0.0.0.0 --port 5000
```

If the dashboard is on a VPS, put it behind nginx with HTTPS and basic auth so the approval links in emails are secure.

---

## Tone / Voice Customization

Edit `REPLY_TONE_NOTES` in `.env` (or modify `config.py`) to adjust Claude's drafting personality. Good additions:
- A couple of example ideal replies so Claude matches the voice exactly
- Specific handling instructions ("always offer to comp dessert on 3-star", "never mention manager's name publicly")

---

## Troubleshooting

| Issue | Fix |
|---|---|
| `403 REQUEST_DENIED` on review list | GBP API access not yet approved — wait for Google |
| OAuth browser doesn't open on server | Run `jolly-roger auth` locally first, then copy `token.json` to the server |
| `409 Conflict` on reply | Someone already replied manually on Google — status set to skipped |
| Gmail SMTP auth fails | Use an App Password, not your account password (requires 2FA) |
