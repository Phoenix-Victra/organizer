"""Flask dashboard — approve, edit, or reject reply drafts."""

import logging
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, flash
from . import db, gbp, config

log = logging.getLogger(__name__)

app = Flask(__name__, template_folder="../templates")
app.secret_key = config.FLASK_SECRET_KEY


@app.route("/")
def index():
    status_filter = request.args.get("status")
    reviews = db.get_reviews(status=status_filter)

    all_reviews = db.get_reviews()
    from collections import Counter
    counter = Counter(r["status"] for r in all_reviews)
    counts = {
        "total": len(all_reviews),
        "new": counter.get("new", 0),
        "drafted": counter.get("drafted", 0),
        "posted": counter.get("posted", 0),
        "rejected": counter.get("rejected", 0),
        "skipped": counter.get("skipped", 0),
    }

    return render_template("index.html", reviews=reviews, status_filter=status_filter, counts=counts)


@app.route("/review/<review_id>")
def review_detail(review_id: str):
    review = db.get_review(review_id)
    if not review:
        flash("Review not found.", "error")
        return redirect(url_for("index"))
    return render_template("review.html", review=review)


@app.route("/review/<review_id>/approve", methods=["POST"])
def approve(review_id: str):
    review = db.get_review(review_id)
    if not review:
        flash("Review not found.", "error")
        return redirect(url_for("index"))

    reply_text = request.form.get("reply", "").strip()
    if not reply_text:
        flash("Reply text cannot be empty.", "error")
        return redirect(url_for("review_detail", review_id=review_id))

    try:
        gbp.post_reply(review_id, reply_text)
    except ValueError as exc:
        flash(f"Could not post: {exc}", "error")
        return redirect(url_for("review_detail", review_id=review_id))
    except Exception as exc:
        log.error("Error posting reply for %s: %s", review_id, exc)
        flash(f"Google API error: {exc}", "error")
        return redirect(url_for("review_detail", review_id=review_id))

    posted_at = datetime.now(timezone.utc).isoformat()
    db.set_status(review_id, "posted", final_reply=reply_text, posted_at=posted_at)
    flash("Reply posted successfully!", "success")
    return redirect(url_for("index"))


@app.route("/review/<review_id>/reject", methods=["POST"])
def reject(review_id: str):
    db.set_status(review_id, "rejected")
    flash("Review marked as rejected — no reply will be posted.", "success")
    return redirect(url_for("index"))
