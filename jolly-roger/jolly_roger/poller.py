"""Core polling loop — fetch new reviews, draft replies, send digest."""

import logging
from datetime import datetime, timezone
from . import db, gbp, drafter, emailer, config

log = logging.getLogger(__name__)


def run(dashboard_url: str = "http://localhost:5000", skip_email: bool = False) -> int:
    """Fetch new reviews, generate drafts, send digest. Returns count of new reviews."""
    db.init_db()

    log.info("Fetching reviews from Google Business Profile…")
    try:
        all_reviews = gbp.list_reviews()
    except Exception as exc:
        log.error("Failed to fetch reviews: %s", exc)
        raise

    known = db.known_ids()
    new_reviews = [r for r in all_reviews if r["review_id"] not in known]
    log.info("%d total reviews fetched, %d new", len(all_reviews), len(new_reviews))

    drafted = []
    for r in new_reviews:
        # Skip reviews that already have a reply (someone replied manually on Google)
        if r.get("has_existing_reply"):
            db.insert_review({**r, "sensitive": 0})
            db.set_status(r["review_id"], "skipped")
            log.info("Skipped %s (reply already exists)", r["review_id"])
            continue

        db.insert_review({**r, "sensitive": 0})

        log.info("Drafting reply for %s (%d★)…", r["review_id"], r["star_rating"])
        try:
            draft, sensitive = drafter.draft_reply(r)
        except Exception as exc:
            log.warning("Draft failed for %s: %s", r["review_id"], exc)
            draft, sensitive = None, r["star_rating"] <= config.SENSITIVE_STAR_THRESHOLD

        db.save_draft(r["review_id"], draft, sensitive)
        drafted.append({**r, "draft_reply": draft, "sensitive": int(sensitive)})

    if not skip_email and drafted:
        try:
            emailer.send_digest(drafted, dashboard_url)
        except Exception as exc:
            log.error("Digest email failed: %s", exc)

    return len(new_reviews)
