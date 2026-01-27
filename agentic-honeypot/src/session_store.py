import json
import os
from typing import List, Dict, Any
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class SessionStore:
    def __init__(self, url: str = REDIS_URL):
        self._r = redis.from_url(url)

    async def append_message(self, session_id: str, message: Dict[str, Any]):
        key = f"session:{session_id}:history"
        await self._r.rpush(key, json.dumps(message))
        # set a reasonable TTL (e.g., 7 days) if not set
        await self._r.expire(key, 7 * 24 * 3600)

    async def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        key = f"session:{session_id}:history"
        items = await self._r.lrange(key, 0, -1)
        return [json.loads(x) for x in items] if items else []

    async def set_extracted(self, session_id: str, extracted: Dict[str, Any]):
        key = f"session:{session_id}:extracted"
        await self._r.set(key, json.dumps(extracted))
        await self._r.expire(key, 7 * 24 * 3600)

    async def get_extracted(self, session_id: str) -> Dict[str, Any]:
        key = f"session:{session_id}:extracted"
        v = await self._r.get(key)
        return json.loads(v) if v else {}
