"""Google Business Profile API wrapper.

Endpoints used:
  List reviews:  GET  mybusinessaccountmanagement.googleapis.com  (account list)
                 GET  mybusiness.googleapis.com/v4/{location}/reviews
  Reply:         PUT  mybusiness.googleapis.com/v4/{location}/reviews/{reviewId}/reply
"""

import logging
from datetime import datetime, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from . import config
from .google_auth import get_credentials

log = logging.getLogger(__name__)

# Base URL for the older v4 surface that has review list + reply
_GBP_V4 = "https://mybusiness.googleapis.com/v4"


def _http():
    """Authorised httplib2.Http object."""
    import httplib2
    creds = get_credentials()
    http = httplib2.Http()
    creds.apply(http.request.__func__)  # attach auth headers
    return http, creds


def list_reviews(page_size: int = 50) -> list[dict]:
    """Return all reviews for the configured location, newest first."""
    creds = get_credentials()
    from googleapiclient.discovery import build
    import httplib2

    # Use raw requests with the access token; the GBP v4 API is not in the
    # standard discovery catalogue, so we call it directly.
    import requests

    headers = {"Authorization": f"Bearer {creds.token}"}
    location = f"{config.GBP_ACCOUNT_ID}/{config.GBP_LOCATION_ID}"
    url = f"{_GBP_V4}/{location}/reviews"
    reviews = []
    next_page = None

    while True:
        params: dict = {"pageSize": page_size, "orderBy": "updateTime desc"}
        if next_page:
            params["pageToken"] = next_page

        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        for r in data.get("reviews", []):
            reviews.append(_normalise(r))

        next_page = data.get("nextPageToken")
        if not next_page:
            break

    return reviews


def post_reply(review_id: str, reply_text: str) -> None:
    """Post (or update) a reply to a review."""
    creds = get_credentials()
    import requests

    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
    }
    location = f"{config.GBP_ACCOUNT_ID}/{config.GBP_LOCATION_ID}"
    url = f"{_GBP_V4}/{location}/reviews/{review_id}/reply"
    body = {"comment": reply_text}

    resp = requests.put(url, headers=headers, json=body, timeout=30)
    if resp.status_code == 409:
        # A reply already exists — don't overwrite a manual one silently
        existing = resp.json().get("error", {}).get("message", "")
        raise ValueError(f"Reply already exists for {review_id}: {existing}")
    resp.raise_for_status()


def _normalise(raw: dict) -> dict:
    """Map GBP API review shape → our internal dict."""
    star_map = {
        "STAR_RATING_UNSPECIFIED": 0,
        "ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5,
    }
    return {
        "review_id": raw["reviewId"],
        "author": raw.get("reviewer", {}).get("displayName", "Anonymous"),
        "star_rating": star_map.get(raw.get("starRating", "STAR_RATING_UNSPECIFIED"), 0),
        "comment": raw.get("comment", ""),
        "created_at": raw.get("createTime", datetime.now(timezone.utc).isoformat()),
        "has_existing_reply": bool(raw.get("reviewReply")),
    }
