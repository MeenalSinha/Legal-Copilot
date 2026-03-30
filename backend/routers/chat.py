"""
Chat Router - AI assistant for document Q&A
"""

import logging
import os
import httpx
import re
from fastapi import APIRouter, HTTPException

from models.schemas import ChatRequest, ChatResponse

router = APIRouter()
logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"


RULE_BASED_RESPONSES = {
    "sell": "Based on the document analysis, look for clauses categorized as 'Data Sharing' with High or Critical risk levels. These typically indicate data sale practices.",
    "safe": "Safety is determined by the overall risk score. A score below 30 suggests relatively safe terms, while above 70 indicates significant risks.",
    "data": "Data collection and sharing clauses are among the most important to review. Check any clauses marked as Critical or High risk in the Data Collection and Data Sharing categories.",
    "delete": "The right to delete your data (right to erasure) should be explicitly stated. Look for User Rights clauses in the analysis.",
    "cancel": "Cancellation terms are typically found in Termination clauses. Review these carefully for notice requirements and refund policies.",
    "refund": "Refund policies are covered under Payment clauses. High-risk payment clauses often indicate no-refund policies.",
    "arbitration": "Arbitration clauses require you to resolve disputes privately rather than in court. These are typically rated as High or Critical risk.",
    "location": "Location data collection is a significant privacy concern. Check Data Collection clauses for location tracking mentions.",
    "third party": "Third-party data sharing is one of the biggest privacy risks. Look for Data Sharing and Third Party Services clauses.",
    "children": "Children's privacy protections (COPPA compliance) should be explicitly stated. Absence of such protections is concerning.",
}


async def query_claude_chat(message: str, context: str, history: list) -> str:
    """Query Claude for conversational responses about the document."""
    if not ANTHROPIC_API_KEY:
        return None

    system_prompt = f"""You are a legal AI assistant helping users understand Terms & Conditions documents.
Be concise, clear, and helpful. Answer in 2-4 sentences. Focus on practical user impact.
Avoid legal jargon. If something is risky, say so clearly.

Document context (analyzed T&C):
{context[:3000] if context else "No document context provided. Answer based on general knowledge."}"""

    messages = []
    for h in history[-6:]:
        messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": message})

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                ANTHROPIC_API_URL,
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 300,
                    "system": system_prompt,
                    "messages": messages
                }
            )
            if response.status_code == 200:
                return response.json()["content"][0]["text"]
    except Exception as e:
        logger.warning(f"Claude chat failed: {e}")

    return None


def rule_based_response(message: str) -> str:
    """Generate rule-based response when AI is unavailable."""
    msg_lower = message.lower()
    for keyword, response in RULE_BASED_RESPONSES.items():
        if keyword in msg_lower:
            return response

    return ("I can help you understand specific aspects of the Terms & Conditions. "
            "Try asking about data sharing, cancellation, arbitration clauses, or whether the document is safe.")


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with AI about the analyzed document."""
    try:
        # Try AI first
        ai_response = await query_claude_chat(
            request.message,
            request.document_context or "",
            [m.model_dump() for m in request.conversation_history]
        )

        response_text = ai_response if ai_response else rule_based_response(request.message)

        return ChatResponse(
            response=response_text,
            confidence=0.92 if ai_response else 0.65
        )

    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(500, "Chat service temporarily unavailable.")
