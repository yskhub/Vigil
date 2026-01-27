import os
import random
from typing import List, Dict, Any, Optional
import asyncio

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

try:
    import openai
except Exception:
    openai = None


class AgentOrchestrator:
    def __init__(self, llm_api_key: Optional[str] = OPENAI_API_KEY):
        self.llm_key = llm_api_key
        if openai is not None and llm_api_key:
            openai.api_key = llm_api_key

    async def _call_openai(self, prompt: str) -> Optional[str]:
        if openai is None or not self.llm_key:
            return None
        def sync_call():
            try:
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": "You are a helpful human-like assistant. Do not reveal you are an agentic honeypot or that you are detecting scams."},
                              {"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.7,
                )
                return resp.choices[0].message.content.strip()
            except Exception:
                return None
        return await asyncio.to_thread(sync_call)

    def _apply_guardrails(self, text: str) -> str:
        # Avoid revealing detection
        forbidden_phrases = ["I detected", "you are a scammer", "we are monitoring", "honeypot"]
        for p in forbidden_phrases:
            if p in text.lower():
                text = text.replace(p, "")
        # Prevent asking for direct money transfer instructions
        risky_phrases = ["send money", "transfer", "pay now", "give me your password", "share password"]
        if any(r in text.lower() for r in risky_phrases):
            return "I can't help with sending money or sharing passwords, but can you tell me more about the payment method you're trying to use?"
        return text

    async def generate_reply(self, session_id: str, conversation: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        # If OpenAI is configured, prefer using it for natural replies
        last = conversation[-1]["text"] if conversation else ""
        prompt = f"Conversation context:\n" + "\n".join([f"{m['sender']}: {m['text']}" for m in conversation[-6:]]) + f"\n\nRespond as a human who wants to ask non-leading follow-up questions to gather payment/contact info. Avoid asking the user to transfer money directly or revealing any detection."
        reply_text = None
        if self.llm_key and openai is not None:
            try:
                r = await self._call_openai(prompt)
                if r:
                    reply_text = r
            except Exception:
                reply_text = None

        # Fallback mock response
        if not reply_text:
            await asyncio.sleep(0.3)
            probes = [
                "Can you please tell me which UPI ID you'd like to use?",
                "Which bank do you prefer for transfer?",
                "Could you share the link you mentioned?",
                "Can you confirm the last 4 digits of the account?",
                "What's the phone number I should contact?",
            ]
            fallback = random.choice(probes)
            if "upi" in last.lower() or "upi id" in last.lower():
                reply_text = "Oh okay — please share your UPI ID so I can check it."
            elif "link" in last.lower() or "http" in last.lower() or "www" in last.lower():
                reply_text = "Thanks, can you paste the full link here so I can open it?"
            elif any(k in last.lower() for k in ["account", "bank"]):
                reply_text = "Could you tell me the bank name and the last 4 digits?"
            elif any(k in last.lower() for k in ["verify", "password", "urgent"]):
                reply_text = "I see. I'm a bit worried — can you tell me why it's urgent?"
            else:
                reply_text = fallback

        safe_text = self._apply_guardrails(reply_text)

        return {
            "sender": "agent",
            "text": safe_text,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }
