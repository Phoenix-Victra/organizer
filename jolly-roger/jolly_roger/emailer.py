"""Send the daily digest email."""

import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import date
from . import config

log = logging.getLogger(__name__)

STARS = {1: "⭐", 2: "⭐⭐", 3: "⭐⭐⭐", 4: "⭐⭐⭐⭐", 5: "⭐⭐⭐⭐⭐"}


def send_digest(reviews: list, dashboard_url: str = "http://localhost:5000") -> None:
    if not reviews:
        log.info("No new reviews — skipping digest email.")
        return

    subject = f"Jolly Roger Reviews — {len(reviews)} new • {date.today()}"
    html = _build_html(reviews, dashboard_url)
    plain = _build_plain(reviews, dashboard_url)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.SMTP_USER
    msg["To"] = config.DIGEST_TO
    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
        server.starttls()
        server.login(config.SMTP_USER, config.SMTP_PASS)
        server.send_message(msg)

    log.info("Digest sent to %s (%d reviews)", config.DIGEST_TO, len(reviews))


def _build_html(reviews: list, dashboard_url: str) -> str:
    rows = []
    for r in reviews:
        sensitive_badge = '<span style="color:#c0392b;font-weight:bold"> ⚠ SENSITIVE</span>' if r["sensitive"] else ""
        draft_html = r["draft_reply"].replace("\n", "<br>") if r["draft_reply"] else "<em>No draft yet</em>"
        rows.append(f"""
        <div style="border:1px solid #ddd;border-radius:6px;padding:16px;margin-bottom:20px;font-family:sans-serif">
          <p><strong>{STARS.get(r['star_rating'], '?')} {r['star_rating']}/5</strong>
             &nbsp;—&nbsp; {r['author']}{sensitive_badge}</p>
          <p style="color:#444">{r['comment'] or '<em>(no written comment)</em>'}</p>
          <hr style="border:none;border-top:1px solid #eee">
          <p style="color:#555"><strong>Suggested reply:</strong></p>
          <p style="background:#f9f9f9;padding:10px;border-left:3px solid #3498db">{draft_html}</p>
          <p><a href="{dashboard_url}/review/{r['review_id']}"
                style="background:#3498db;color:#fff;padding:8px 14px;border-radius:4px;text-decoration:none">
             Review &amp; Approve →</a></p>
        </div>""")

    return f"""<!DOCTYPE html><html><body>
    <h2 style="font-family:sans-serif">Jolly Roger — {len(reviews)} new review(s)</h2>
    {''.join(rows)}
    <p style="font-family:sans-serif;color:#999;font-size:12px">
      Visit the <a href="{dashboard_url}">full dashboard</a> to approve, edit, or reject replies.
    </p>
    </body></html>"""


def _build_plain(reviews: list, dashboard_url: str) -> str:
    lines = [f"Jolly Roger — {len(reviews)} new review(s)\n"]
    for r in reviews:
        flag = " [SENSITIVE]" if r["sensitive"] else ""
        lines.append(f"{'='*60}")
        lines.append(f"{r['star_rating']}/5 — {r['author']}{flag}")
        lines.append(r["comment"] or "(no written comment)")
        lines.append("")
        lines.append("Suggested reply:")
        lines.append(r["draft_reply"] or "(no draft)")
        lines.append(f"\nApprove/edit: {dashboard_url}/review/{r['review_id']}\n")
    lines.append(f"Full dashboard: {dashboard_url}")
    return "\n".join(lines)
