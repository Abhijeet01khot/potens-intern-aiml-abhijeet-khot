from typing import Dict, List, Any
from datetime import datetime


# Mock policy knowledge base.
# In a real product, this could come from database, CRM, policy docs, or internal APIs.
POLICY_KNOWLEDGE_BASE = {
    "billing": {
        "sla": "Billing-related issues should receive a first response within 2 business hours.",
        "owner": "Finance Support Team",
        "rule": "Payment deducted, refund, failed payment, invoice, and duplicate charge issues must be checked with transaction details."
    },
    "technical": {
        "sla": "Technical issues should receive a first response within 4 business hours.",
        "owner": "Technical Support Team",
        "rule": "App crash, login error, broken feature, and system downtime issues must include device/app/browser details."
    },
    "account": {
        "sla": "Account access issues should receive a first response within 2 business hours.",
        "owner": "Account Recovery Team",
        "rule": "Blocked accounts, password reset failures, suspicious login, and verification problems require identity verification."
    },
    "delivery": {
        "sla": "Delivery or service delay issues should receive a first response within 6 business hours.",
        "owner": "Operations Team",
        "rule": "Delayed delivery, missed appointment, and service not completed issues require order/service ID."
    },
    "refund": {
        "sla": "Refund and cancellation issues should receive a first response within 3 business hours.",
        "owner": "Refund Desk",
        "rule": "Refund requests must be checked against payment status, cancellation window, and service completion status."
    },
    "general": {
        "sla": "General questions should receive a first response within 1 business day.",
        "owner": "Customer Support Team",
        "rule": "General requests can be handled by standard support unless they include money, security, or service disruption."
    }
}


# Mock past tickets.
# This supports the similar-past-input search tool.
PAST_TICKETS = [
    {
        "id": "TKT-1001",
        "text": "Payment was deducted but order was not confirmed.",
        "category": "billing",
        "priority": "P1",
        "resolution": "Verified payment gateway status and manually confirmed the order."
    },
    {
        "id": "TKT-1002",
        "text": "Unable to login because OTP is not received.",
        "category": "account",
        "priority": "P1",
        "resolution": "Checked SMS provider logs and asked user to retry after number verification."
    },
    {
        "id": "TKT-1003",
        "text": "The mobile app keeps crashing after the latest update.",
        "category": "technical",
        "priority": "P1",
        "resolution": "Collected device logs and escalated bug to engineering."
    },
    {
        "id": "TKT-1004",
        "text": "Delivery is delayed by three days and no update is visible.",
        "category": "delivery",
        "priority": "P1",
        "resolution": "Contacted operations team and updated customer with revised ETA."
    },
    {
        "id": "TKT-1005",
        "text": "I want to cancel my subscription and get refund.",
        "category": "refund",
        "priority": "P2",
        "resolution": "Checked refund policy and processed cancellation request."
    },
    {
        "id": "TKT-1006",
        "text": "Need information about available plans and pricing.",
        "category": "general",
        "priority": "P2",
        "resolution": "Shared product pricing page and plan comparison."
    }
]


def lookup_policy_tool(category: str) -> Dict[str, Any]:
    """
    Looks up internal handling policy for a ticket category.
    This is a real callable tool because the agent calls this function
    and receives structured data back.
    """
    normalized_category = category.lower().strip()

    policy = POLICY_KNOWLEDGE_BASE.get(
        normalized_category,
        POLICY_KNOWLEDGE_BASE["general"]
    )

    return {
        "tool_name": "lookup_policy_tool",
        "input": {"category": category},
        "output": {
            "category": normalized_category,
            "sla": policy["sla"],
            "owner": policy["owner"],
            "rule": policy["rule"]
        },
        "called_at": datetime.now().isoformat(timespec="seconds")
    }


def search_similar_ticket_tool(ticket_text: str) -> Dict[str, Any]:
    """
    Searches similar past tickets using simple word-overlap scoring.
    It is intentionally lightweight for the take-home assignment.
    """
    query_words = set(ticket_text.lower().split())
    scored_tickets: List[Dict[str, Any]] = []

    for ticket in PAST_TICKETS:
        ticket_words = set(ticket["text"].lower().split())
        overlap = len(query_words.intersection(ticket_words))

        scored_tickets.append({
            "id": ticket["id"],
            "text": ticket["text"],
            "category": ticket["category"],
            "priority": ticket["priority"],
            "resolution": ticket["resolution"],
            "similarity_score": overlap
        })

    scored_tickets.sort(key=lambda item: item["similarity_score"], reverse=True)
    best_match = scored_tickets[0]

    return {
        "tool_name": "search_similar_ticket_tool",
        "input": {"ticket_text": ticket_text},
        "output": {
            "best_match": best_match,
            "note": "Similarity is based on word overlap for this 24-hour assignment version."
        },
        "called_at": datetime.now().isoformat(timespec="seconds")
    }


def draft_acknowledgement_tool(
    category: str,
    priority: str,
    user_text: str
) -> Dict[str, Any]:
    """
    Drafts a customer-facing acknowledgement message.
    """
    category_clean = category.replace("_", " ").title()

    if priority == "P0":
        tone = "urgent"
        message = (
            f"We have received your {category_clean} issue and marked it as urgent. "
            "Our team will review it immediately and contact you with the next update."
        )
    elif priority == "P1":
        tone = "high priority"
        message = (
            f"We have received your {category_clean} issue and marked it as high priority. "
            "Our support team will check the details and update you as soon as possible."
        )
    else:
        tone = "standard"
        message = (
            f"We have received your {category_clean} request. "
            "Our team will review it and get back to you with the required information."
        )

    return {
        "tool_name": "draft_acknowledgement_tool",
        "input": {
            "category": category,
            "priority": priority,
            "user_text": user_text
        },
        "output": {
            "tone": tone,
            "draft_message": message
        },
        "called_at": datetime.now().isoformat(timespec="seconds")
    }


def human_escalation_tool(reason: str) -> Dict[str, Any]:
    """
    Stretch feature: human-in-the-loop escalation when confidence is low
    or when the issue is very urgent.
    """
    return {
        "tool_name": "human_escalation_tool",
        "input": {"reason": reason},
        "output": {
            "escalated": True,
            "assigned_to": "Human Support Lead",
            "note": "This case should be reviewed by a human before final action."
        },
        "called_at": datetime.now().isoformat(timespec="seconds")
    }