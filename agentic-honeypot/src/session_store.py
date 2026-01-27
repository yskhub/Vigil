import json
import os
from typing import List, Dict, Any

try:
    import redis.asyncio as redis
except Exception:
    redis = None

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


class SessionStore:
    def __init__(self, url: str = REDIS_URL):
        self._use_redis = False
        self._in_memory: Dict[str, List[Dict[str, Any]]] = {}
        self._in_memory_extracted: Dict[str, Dict[str, Any]] = {}
        if redis is not None:
            try:
                self._r = redis.from_url(url)
                # don't await ping here; lazy connect
                self._use_redis = True
            except Exception:
                self._use_redis = False

    async def append_message(self, session_id: str, message: Dict[str, Any]):
        key = f"session:{session_id}:history"
        if self._use_redis:
            try:
                await self._r.rpush(key, json.dumps(message))
                await self._r.expire(key, 7 * 24 * 3600)
                return
            except Exception:
                self._use_redis = False
        # fallback in-memory
        self._in_memory.setdefault(session_id, []).append(message)

    async def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        key = f"session:{session_id}:history"
        if self._use_redis:
            try:
                items = await self._r.lrange(key, 0, -1)
                return [json.loads(x) for x in items] if items else []
            except Exception:
                self._use_redis = False
        return list(self._in_memory.get(session_id, []))

    async def set_extracted(self, session_id: str, extracted: Dict[str, Any]):
        key = f"session:{session_id}:extracted"
        if self._use_redis:
            try:
                await self._r.set(key, json.dumps(extracted))
                await self._r.expire(key, 7 * 24 * 3600)
                return
            except Exception:
                self._use_redis = False
        self._in_memory_extracted[session_id] = extracted

    async def get_extracted(self, session_id: str) -> Dict[str, Any]:
        key = f"session:{session_id}:extracted"
        if self._use_redis:
            try:
                v = await self._r.get(key)
                return json.loads(v) if v else {}
            except Exception:
                self._use_redis = False
        return self._in_memory_extracted.get(session_id, {})
