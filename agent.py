import json
import os
from typing import Dict, Any, List

import google.generativeai as genai
from dotenv import load_dotenv

from tools import (
    lookup_policy_tool,
    search_similar_ticket_tool,
    draft_acknowledgement_tool,
    human_escalation_tool,
)

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


CATEGORIES = [
    "billing",
    "technical",
    "account",
    "delivery",
    "refund",
    "general",
]

PRIORITIES = {
    "P0": "Critical issue that needs immediate human attention, such as fraud, security risk, complete outage, or severe customer impact.",
    "P1": "Important issue that should be handled quickly, such as payment deducted, account blocked, repeated failure, or delayed service.",
    "P2": "Normal request or low-risk issue, such as general question, plan information, or simple update request.",
}


def _fallback_rule_based_triage(ticket_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Backup triage path if Gemini API is missing or unavailable.
    This keeps the application usable during demos.
    """
    text = ticket_text.lower()

    category = "general"
    priority = "P2"
    confidence = 0.55

    if any(word in text for word in ["payment", "paid", "deducted", "charged", "invoice"]):
        category = "billing"
        priority = "P1"
        confidence = 0.78
    elif any(word in text for word in ["refund", "cancel", "cancellation"]):
        category = "refund"
        priority = "P2"
        confidence = 0.76
    elif any(word in text for word in ["login", "password", "otp", "account", "blocked"]):
        category = "account"
        priority = "P1"
        confidence = 0.80
    elif any(word in text for word in ["crash", "error", "bug", "not working", "down"]):
        category = "technical"
        priority = "P1"
        confidence = 0.77
    elif any(word in text for word in ["delivery", "delayed", "late", "not received"]):
        category = "delivery"
        priority = "P1"
        confidence = 0.75

    if any(word in text for word in ["fraud", "hacked", "security", "urgent", "emergency"]):
        priority = "P0"
        confidence = max(confidence, 0.86)

    return {
        "category": category,
        "priority": priority,
        "confidence": confidence,
        "reasoning": (
            "Fallback triage was used because the LLM was unavailable. "
            "The category and priority were selected using simple keyword rules."
        ),
        "why": (
            f"The ticket was mapped to {category} with priority {priority} "
            "based on the issue type and urgency indicators in the text."
        ),
        "next_tool": "lookup_policy_tool",
    }


def _call_gemini_triage(ticket_text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calls Gemini to make the triage decision.
    The model only decides the structured triage result.
    Actual tool execution happens in Python functions below.
    """
    genai.configure(api_key=GEMINI_API_KEY)

    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = f"""
You are a support-ticket triage agent.

Your job:
Classify the ticket into one category, one priority, and choose the next tool.

Allowed categories:
{CATEGORIES}

Priority scheme:
{json.dumps(PRIORITIES, indent=2)}

Allowed next_tool values:
- lookup_policy_tool
- search_similar_ticket_tool
- draft_acknowledgement_tool
- human_escalation_tool

Rules:
- Return only valid JSON.
- Do not include markdown.
- Choose P0 only for urgent, fraud, security, safety, complete outage, or severe customer impact.
- Choose P1 for payment issues, blocked account, repeated technical failure, or delayed service.
- Choose P2 for normal requests and general questions.
- Use human_escalation_tool if confidence is below 0.60 or the case is P0.
- Include clear reasoning and why explanation.
- Confidence must be between 0 and 1.

Ticket text:
{ticket_text}

Optional metadata:
{json.dumps(metadata, indent=2)}

Required JSON format:
{{
  "category": "billing",
  "priority": "P1",
  "confidence": 0.82,
  "next_tool": "lookup_policy_tool",
  "reasoning": "Short reasoning trace explaining classification.",
  "why": "Customer-facing explanation of why this decision was made."
}}
"""

    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    # Clean accidental markdown wrapping if the model adds it.
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    return json.loads(raw_text)


def run_triage_agent(ticket_text: str, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """
    Main agent function.
    It gets a triage decision, executes real tools, and returns full trace.
    """
    if metadata is None:
        metadata = {}

    reasoning_trace: List[Dict[str, Any]] = []

    reasoning_trace.append({
        "step": 1,
        "name": "input_received",
        "details": {
            "ticket_text": ticket_text,
            "metadata": metadata,
        },
    })

    try:
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your_actual_api_key_here":
            triage = _fallback_rule_based_triage(ticket_text, metadata)
            model_used = "fallback_rule_based"
        else:
            triage = _call_gemini_triage(ticket_text, metadata)
            model_used = "gemini-1.5-flash"

    except Exception as error:
        triage = _fallback_rule_based_triage(ticket_text, metadata)
        model_used = "fallback_rule_based_after_error"
        reasoning_trace.append({
            "step": 2,
            "name": "llm_error",
            "details": {
                "error": str(error),
                "fallback_used": True,
            },
        })

    reasoning_trace.append({
        "step": 3,
        "name": "triage_decision_created",
        "details": {
            "model_used": model_used,
            "triage": triage,
        },
    })

    category = triage.get("category", "general")
    priority = triage.get("priority", "P2")
    confidence = float(triage.get("confidence", 0.50))
    next_tool = triage.get("next_tool", "lookup_policy_tool")

    tool_results = []

    # Tool 1: policy lookup is always useful.
    policy_result = lookup_policy_tool(category)
    tool_results.append(policy_result)

    reasoning_trace.append({
        "step": 4,
        "name": "tool_called",
        "details": policy_result,
    })

    # Tool 2: similar ticket search gives operational context.
    similar_ticket_result = search_similar_ticket_tool(ticket_text)
    tool_results.append(similar_ticket_result)

    reasoning_trace.append({
        "step": 5,
        "name": "tool_called",
        "details": similar_ticket_result,
    })

    # Tool 3: draft acknowledgement prepares the customer response.
    acknowledgement_result = draft_acknowledgement_tool(
        category=category,
        priority=priority,
        user_text=ticket_text,
    )
    tool_results.append(acknowledgement_result)

    reasoning_trace.append({
        "step": 6,
        "name": "tool_called",
        "details": acknowledgement_result,
    })

    # Stretch: escalate if P0 or confidence is low.
    if priority == "P0" or confidence < 0.60 or next_tool == "human_escalation_tool":
        escalation_result = human_escalation_tool(
            reason=f"Priority={priority}, confidence={confidence}"
        )
        tool_results.append(escalation_result)

        reasoning_trace.append({
            "step": 7,
            "name": "tool_called",
            "details": escalation_result,
        })

    final_output = {
        "category": category,
        "priority": priority,
        "next_tool": next_tool,
        "confidence": confidence,
        "reasoning": triage.get("reasoning", ""),
        "why": triage.get("why", ""),
        "tool_results": tool_results,
        "reasoning_trace": reasoning_trace,
    }

    return final_output