from typing import Dict, Any


def baseline_classifier(ticket_text: str) -> Dict[str, Any]:
    """
    Simple baseline classifier.

    This is intentionally basic. It does not call tools and does not create
    a reasoning trace. It is used only for comparison against the agentic flow.
    """
    text = ticket_text.lower()

    category = "general"
    priority = "P2"

    if any(word in text for word in ["payment", "paid", "deducted", "charged", "invoice"]):
        category = "billing"
        priority = "P1"

    elif any(word in text for word in ["refund", "cancel", "cancellation"]):
        category = "refund"
        priority = "P2"

    elif any(word in text for word in ["login", "password", "otp", "account", "blocked"]):
        category = "account"
        priority = "P1"

    elif any(word in text for word in ["crash", "error", "bug", "not working", "down"]):
        category = "technical"
        priority = "P1"

    elif any(word in text for word in ["delivery", "delayed", "late", "not received"]):
        category = "delivery"
        priority = "P1"

    if any(word in text for word in ["fraud", "hacked", "security", "urgent", "emergency"]):
        priority = "P0"

    return {
        "category": category,
        "priority": priority,
        "method": "baseline_keyword_classifier",
        "note": "This baseline uses simple keyword checks and does not call any tools."
    }


if __name__ == "__main__":
    sample = "My payment was deducted but my order is not showing."
    print(baseline_classifier(sample))