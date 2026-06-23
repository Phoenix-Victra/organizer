"""Use Claude to draft a reply and flag sensitive reviews."""

import anthropic
from . import config

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    return _client


def draft_reply(review: dict) -> tuple[str, bool]:
    """Return (draft_text, is_sensitive).

    is_sensitive is True when the review warrants extra human care before
    any reply is sent (very low stars, illness, legal language, etc.).
    """
    stars = review.get("star_rating", 0)
    author = review.get("author", "the guest")
    comment = review.get("comment", "").strip() or "(no written comment)"

    sensitive_flag = stars <= config.SENSITIVE_STAR_THRESHOLD

    user_msg = f"""Review details:
- Author: {author}
- Star rating: {stars}/5
- Comment: {comment}

Please draft a reply following the tone guidelines.

Also, on a new line at the very end, output exactly one of:
SENSITIVE: yes
SENSITIVE: no

Output only the reply text and that final line — no other commentary."""

    resp = _get_client().messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=400,
        system=config.REPLY_TONE,
        messages=[{"role": "user", "content": user_msg}],
    )

    full = resp.content[0].text.strip()

    # Parse the SENSITIVE marker Claude appended
    lines = full.splitlines()
    claude_sensitive = False
    reply_lines = []
    for line in lines:
        if line.strip().upper().startswith("SENSITIVE:"):
            claude_sensitive = "YES" in line.upper()
        else:
            reply_lines.append(line)

    draft = "\n".join(reply_lines).strip()
    is_sensitive = sensitive_flag or claude_sensitive
    return draft, is_sensitive
