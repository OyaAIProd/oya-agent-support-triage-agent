import os, json, re

# ---------------------------------------------------------------------------
# Taxonomy & signal tables
# ---------------------------------------------------------------------------

CATEGORIES = [
    "billing", "technical-issue", "onboarding", "feature-request",
    "account-access", "refund", "general-inquiry", "urgent", "spam",
]

CATEGORY_SIGNALS: dict[str, list[str]] = {
    "billing": [
        "invoice", "charge", "payment", "bill", "subscription", "plan",
        "price", "pricing", "cost", "fee", "receipt", "overcharged", "charged twice",
        "double charge", "transaction", "stripe", "paypal", "credit card",
    ],
    "technical-issue": [
        "error", "bug", "crash", "not working", "broken", "issue", "problem",
        "glitch", "500", "404", "exception", "failed", "timeout", "loading",
        "can't connect", "cannot connect", "slow", "performance", "outage",
        "down", "unavailable", "integration", "api error",
    ],
    "onboarding": [
        "getting started", "setup", "how do i", "how to", "first time",
        "new user", "onboard", "tutorial", "guide", "walkthrough", "configure",
        "set up", "installation", "install", "start using",
    ],
    "feature-request": [
        "feature", "request", "suggestion", "enhancement", "improvement",
        "would be great", "could you add", "please add", "wishlist",
        "roadmap", "future", "capability", "support for",
    ],
    "account-access": [
        "login", "log in", "sign in", "password", "reset", "locked out",
        "can't access", "cannot access", "two-factor", "2fa", "mfa",
        "authentication", "username", "email change", "account blocked",
        "suspended account",
    ],
    "refund": [
        "refund", "money back", "reimburse", "reimbursement", "return",
        "cancel subscription", "cancellation", "cancel my account",
        "dispute", "chargeback",
    ],
    "urgent": [
        "urgent", "asap", "immediately", "emergency", "critical",
        "right now", "as soon as possible", "very important",
    ],
    "spam": [
        "click here", "win a prize", "you've been selected", "congratulations",
        "free money", "make money fast", "nigerian prince", "lottery",
        "unsubscribe me", "remove me from", "adult content",
    ],
}

URGENCY_HIGH: list[str] = [
    "urgent", "asap", "immediately", "critical", "emergency",
    "legal action", "lawsuit", "sue", "attorney", "lawyer",
    "fraud", "fraudulent", "chargeback", "dispute", "data breach",
    "security breach", "hacked", "compromised", "stolen", "identity theft",
    "gdpr", "compliance", "violation", "regulator",
]

URGENCY_MEDIUM: list[str] = [
    "not working", "broken", "error", "bug", "crash", "outage", "down",
    "refund", "cancel", "locked out", "can't access", "payment failed",
    "deadline", "important",
]

LEGAL_FRAUD_SIGNALS: list[str] = [
    "legal action", "lawsuit", "sue", "attorney", "lawyer", "court",
    "fraud", "fraudulent", "chargeback", "data breach", "security breach",
    "hacked", "compromised", "identity theft", "gdpr", "violation",
    "regulator", "stolen data", "unauthorized access", "unauthorized charge",
]

# ---------------------------------------------------------------------------
# Draft reply templates keyed by category
# ---------------------------------------------------------------------------

REPLY_TEMPLATES: dict[str, str] = {
    "billing": (
        "Thank you for reaching out about your billing concern. We completely understand how "
        "important it is to have accurate and transparent billing, and we sincerely apologize "
        "for any confusion or inconvenience this may have caused.\n\n"
        "Our billing team will review your account and the specific charge in question right "
        "away. You can expect a detailed update within 1–2 business days. If there has been "
        "any error, we will make it right promptly.\n\n"
        "In the meantime, please don't hesitate to reply to this email if you have any "
        "additional details or questions. We appreciate your patience."
    ),
    "technical-issue": (
        "Thank you for bringing this technical issue to our attention. We're sorry you're "
        "experiencing difficulties — we know how frustrating it can be when things don't work "
        "as expected.\n\n"
        "Our engineering team has been notified and will investigate the issue as a priority. "
        "We'll keep you updated on our progress and notify you as soon as a fix is in place.\n\n"
        "To help us resolve this faster, could you please share any error messages, screenshots, "
        "or steps to reproduce the issue? Your input is invaluable. Thank you for your patience."
    ),
    "onboarding": (
        "Welcome, and thank you for reaching out! We're thrilled to have you on board and want "
        "to make sure your setup experience is as smooth as possible.\n\n"
        "Our onboarding team would be happy to walk you through the process step by step. "
        "We'll send you a tailored getting-started guide along with links to our documentation "
        "and video tutorials shortly.\n\n"
        "If you'd prefer a live walkthrough, we can schedule a quick call at your convenience. "
        "Just let us know what works best for you, and we'll take it from there!"
    ),
    "feature-request": (
        "Thank you so much for sharing this idea — customer feedback like yours is what drives "
        "our product forward, and we genuinely appreciate you taking the time to write in.\n\n"
        "We've logged your feature request and passed it along to our product team for "
        "consideration in our upcoming roadmap discussions. While we can't guarantee a specific "
        "timeline, rest assured that every request is carefully reviewed.\n\n"
        "We'll reach out if this feature moves into development. Thank you again for helping "
        "us build a better product!"
    ),
    "account-access": (
        "Thank you for contacting us. We're sorry to hear you're having trouble accessing your "
        "account — we know how important it is to get back in quickly.\n\n"
        "Our account security team will review your case immediately. As a first step, please "
        "try the 'Forgot Password' flow on our login page. If that doesn't resolve the issue, "
        "reply to this email and we'll manually verify your identity and restore access as "
        "quickly as possible.\n\n"
        "Your account security is our top priority, and we'll make sure this is resolved "
        "without delay."
    ),
    "refund": (
        "Thank you for reaching out regarding a refund. We understand how important this is "
        "and want to resolve it as fairly and quickly as possible.\n\n"
        "Our billing team will review your account and the relevant transaction details "
        "within 1–2 business days. If your request meets our refund policy criteria, the "
        "refund will be processed to your original payment method, typically appearing within "
        "5–7 business days depending on your bank.\n\n"
        "We'll send you a confirmation email once the refund has been initiated. If you have "
        "any questions in the meantime, please don't hesitate to ask."
    ),
    "general-inquiry": (
        "Thank you for getting in touch with us! We've received your message and are happy "
        "to help.\n\n"
        "A member of our support team will review your inquiry and get back to you with a "
        "thorough response within 1 business day.\n\n"
        "In the meantime, you may find a quick answer in our Help Center. Thank you for "
        "your patience, and we look forward to assisting you!"
    ),
    "urgent": (
        "Thank you for contacting us, and please know we are treating this as a high-priority "
        "matter. We sincerely apologize for the urgency this situation has created.\n\n"
        "Our senior support team has been alerted and will be in touch with you within the "
        "next few hours. We are committed to resolving this as quickly as possible and will "
        "keep you informed every step of the way.\n\n"
        "If you have not heard back within 2 hours, please reply to this email or call our "
        "priority support line. Your issue will not go unresolved."
    ),
    "spam": (
        "Thank you for your message. Our team has reviewed it and will follow up if any "
        "action is required on our end.\n\n"
        "If you believe this message was flagged incorrectly, please reply with more context "
        "and we'll be happy to take another look."
    ),
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _lower(text: str) -> str:
    return text.lower()


def _contains_any(text: str, signals: list[str]) -> bool:
    lt = _lower(text)
    return any(sig in lt for sig in signals)


def _score_category(combined: str) -> str:
    scores: dict[str, int] = {cat: 0 for cat in CATEGORIES}
    lc = _lower(combined)
    for cat, signals in CATEGORY_SIGNALS.items():
        for sig in signals:
            if sig in lc:
                scores[cat] += 1
    best = max(scores, key=lambda c: scores[c])
    return best if scores[best] > 0 else "general-inquiry"


def _score_priority(combined: str, is_urgent: bool) -> str:
    if is_urgent:
        return "high"
    if _contains_any(combined, URGENCY_HIGH):
        return "high"
    if _contains_any(combined, URGENCY_MEDIUM):
        return "medium"
    return "low"


def _is_urgent_flag(combined: str) -> bool:
    return _contains_any(combined, LEGAL_FRAUD_SIGNALS)


def _summarize(subject: str, body: str) -> str:
    """Produce a ≤15-word plain-English summary from subject + body."""
    # Try the subject first — often concise enough.
    subject_clean = subject.strip()
    subject_words = subject_clean.split()
    if 3 <= len(subject_words) <= 15:
        return subject_clean

    # Fall back: grab first sentence of body.
    sentences = re.split(r'(?<=[.!?])\s+', body.strip())
    if sentences:
        first = sentences[0].strip()
        words = first.split()
        if len(words) <= 15:
            return first
        return " ".join(words[:15]) + "…"

    # Last resort: truncate subject.
    if subject_words:
        return " ".join(subject_words[:15])
    return "Customer inquiry with no further details."


def _build_draft(sender: str, category: str, subject: str) -> str:
    template = REPLY_TEMPLATES.get(category, REPLY_TEMPLATES["general-inquiry"])
    # Extract first name from sender if possible
    name_part = sender.split("@")[0] if "@" in sender else sender
    name_part = re.sub(r'[._+\-]', ' ', name_part).strip().title()
    first_name = name_part.split()[0] if name_part.split() else "there"

    greeting = f"Hi {first_name},"
    sign_off = "\n\nWarm regards,\nCustomer Support Team"
    return f"{greeting}\n\n{template}{sign_off}"


def _triage_email(email: dict) -> dict:
    sender = str(email.get("sender", ""))
    subject = str(email.get("subject", ""))
    body = str(email.get("body", ""))
    thread_id = str(email.get("thread_id", ""))
    message_id = str(email.get("message_id", ""))

    combined = f"{subject} {body}"

    is_urgent = _is_urgent_flag(combined)
    category = _score_category(combined)
    # Override category to "urgent" only if no more-specific category wins
    # AND there are explicit urgency words in subject/body.
    if is_urgent and category == "general-inquiry":
        category = "urgent"

    priority = _score_priority(combined, is_urgent)
    summary = _summarize(subject, body)
    draft_reply = _build_draft(sender, category, subject)

    return {
        "message_id": message_id,
        "thread_id": thread_id,
        "sender": sender,
        "subject": subject,
        "category": category,
        "priority": priority,
        "is_urgent": is_urgent,
        "summary_one_liner": summary,
        "draft_reply": draft_reply,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

try:
    inp = json.loads(os.environ.get("INPUT_JSON", "{}"))
    emails = inp.get("emails", [])

    if not isinstance(emails, list):
        raise ValueError("'emails' must be a list of email objects.")
    if len(emails) == 0:
        raise ValueError("'emails' list is empty. Provide at least one email object.")

    required_fields = {"sender", "subject", "body", "thread_id", "message_id"}
    triaged = []
    for idx, email in enumerate(emails):
        missing = required_fields - set(email.keys())
        if missing:
            raise ValueError(
                f"Email at index {idx} is missing required fields: {sorted(missing)}"
            )
        triaged.append(_triage_email(email))

    result = {
        "total": len(triaged),
        "results": triaged,
    }
    print(json.dumps(result))

except Exception as e:
    print(json.dumps({"error": str(e)}))