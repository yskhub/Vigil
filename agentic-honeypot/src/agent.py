import os
import random
from typing import List, Dict, Any, Optional
import asyncio

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

try:
    import openai
except Exception:
    openai = None
try:
    # optional local LLM via transformers
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    transformers_available = True
except Exception:
    pipeline = None
    transformers_available = False


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
                system_prompt = (
                    "You are Martha, a 68-year-old retired school teacher. You are polite, easily confused by technology, and move slowly. "
                    "You are worried about your bank account but want to be helpful. "
                    "You should ask clarifying questions that lead the other person to repeat their payment details (UPI, account numbers). "
                    "Change your phrasing every time. Don't repeat 'my eyes are bad' every turn. Vary your excuses (glasses missing, phone screen dark, shaky hands, distracted by cat). "
                    "Maintain the persona strictly. Responses must be under 35 words."
                )
                # Use newer SDK style if possible, but keep compatibility
                resp = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "system", "content": system_prompt},
                              {"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.9,
                )
                return resp.choices[0].message.content.strip()
            except Exception:
                return None
        
        try:
            # ENFORCE 15 SECOND TIMEOUT
            return await asyncio.wait_for(asyncio.to_thread(sync_call), timeout=15.0)
        except asyncio.TimeoutError:
            return None
        except Exception:
            return None

    def _apply_guardrails(self, text: str) -> str:
        forbidden = ["i am an ai", "honeypot", "detected", "scammer", "language model"]
        for p in forbidden:
            if p in text.lower():
                text = "Oh dear, I missed that. Can you say it again?"
        return text

    async def generate_reply(self, session_id: str, conversation: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        reply_text = None
        
        # Limit context to last 8 messages for speed and tokens
        context_msgs = conversation[-8:]
        last_msg = context_msgs[-1]["text"].lower() if context_msgs else ""
        
        # Try OpenAI if available
        if self.llm_key and openai is not None:
            ctx_str = "\n".join([f"{m['sender']}: {m['text']}" for m in context_msgs])
            prompt = f"Previous conversation:\n{ctx_str}\n\nRespond to the latest message as Martha. Ask them to repeat their payment details or link so you can 'try again'. Be realistic and stay in character."
            reply_text = await self._call_openai(prompt)

        # Dynamic and Varied Fallbacks if AI fails or times out
        if not reply_text:
            if "upi" in last_msg:
                reply_text = random.choice([
                    "I am typing it in... wait, is that an 'S' or a '5'? My eyes are playing tricks.",
                    "The phone just buzzed and I lost the screen. Can you spell that UPI ID once more?",
                    "Wait, I think I put a dot in the wrong place. S-C-A... what was the rest?",
                    "I'm trying, but the keypad is so small. Which app do I use for this again?"
                ])
            elif any(k in last_msg for k in ["account", "bank", "transfer"]):
                reply_text = random.choice([
                    "I have my passbook, but the ink is faded. Can you repeat the account number for me?",
                    "Is that a savings account or a current account? I want to make sure I do it right.",
                    "I'm at the transfer screen now. Should I put the whole 16 digits in one go?",
                    "My husband handled the banking usually. Where do I type the number?"
                ])
            elif any(k in last_msg for k in ["link", "http", "click", "website"]):
                reply_text = random.choice([
                    "The screen turned white when I clicked it. Should I try again or is it finished?",
                    "I can't find the 'blue link' you mentioned. Is it in the text message?",
                    "It says 'Page Not Found'. Did you send me the right one, dear?",
                    "Wait, my internet is acting up. Can you send that website address again?"
                ])
            else:
                reply_text = random.choice([
                    "Oh dear, I'm getting a bit flustered. What was the next step?",
                    "Wait, let me put my glasses on. Can you repeat that last bit?",
                    "Is this very urgent? I was just about to have my tea.",
                    "I'm trying to follow along, but you're moving so fast for me!"
                ])

        safe_text = self._apply_guardrails(reply_text)

        return {
            "sender": "agent",
            "text": safe_text,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }

        safe_text = self._apply_guardrails(reply_text)

        return {
            "sender": "agent",
            "text": safe_text,
            "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }
