import os
import random
from typing import List, Dict, Any, Optional
import asyncio

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class AgentOrchestrator:
    def __init__(self, llm_api_key: Optional[str] = OPENAI_API_KEY):
        self.llm_key = llm_api_key

    async def generate_reply(self, session_id: str, conversation: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        # If an OpenAI key is provided, you could call OpenAI here.
        # For the prototype, provide a deterministic mock reply based on latest message.
        await asyncio.sleep(0.5)  # simulate thinking
        last = conversation[-1]["text"] if conversation else ""
        # Simple heuristics to craft a human-like probing reply
        probes = [
            "Can you please tell me which UPI ID you'd like to use?",
            "Which bank do you prefer for transfer?",
            "Could you share the link you mentioned?",
            "Can you confirm the last 4 digits of the account?",
            "What's the phone number I should contact?",
        ]
        fallback = random.choice(probes)
        if "upi" in last.lower() or "upi id" in last.lower():
            reply = "Oh okay — please share your UPI ID so I can check it."
        elif "link" in last.lower() or "http" in last.lower() or "www" in last.lower():
            reply = "Thanks, can you paste the full link here so I can open it?"
        elif any(k in last.lower() for k in ["account", "bank"]):
            reply = "Could you tell me the bank name and the last 4 digits?"
        elif any(k in last.lower() for k in ["verify", "password", "urgent"]):
            reply = "I see. I'm a bit worried — can you tell me why it's urgent?"
        else:
            reply = fallback

        return {
            "sender": "agent",
            "text": reply,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }
