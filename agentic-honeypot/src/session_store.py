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
                # update last seen time
                await self._r.set(f"session:{session_id}:last", json.dumps({"ts": __import__("time").time()}))
                return
            except Exception:
                self._use_redis = False
        # fallback in-memory
        self._in_memory.setdefault(session_id, []).append(message)
        self._in_memory.setdefault(session_id, [])
        self._in_memory_extracted.setdefault(session_id, self._in_memory_extracted.get(session_id, {}))
        self._in_memory.setdefault(session_id, self._in_memory.get(session_id, []))
        # update last seen time
        self._in_memory.setdefault("_last", {})
        self._in_memory["_last"][session_id] = __import__("time").time()

    async def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        key = f"session:{session_id}:history"
        if self._use_redis:
            try:
                items = await self._r.lrange(key, 0, -1)
                return [json.loads(x) for x in items] if items else []
            except Exception:
                self._use_redis = False
        return list(self._in_memory.get(session_id, []))

    async def get_total_messages(self, session_id: str) -> int:
        hist = await self.get_history(session_id)
        return len(hist)

    async def list_sessions(self) -> List[str]:
        sessions = set()
        if self._use_redis:
            try:
                keys = await self._r.keys("session:*:history")
                for k in keys:
                    s = k.decode() if isinstance(k, bytes) else k
                    # s = session:SESSIONID:history
                    parts = s.split(":")
                    if len(parts) >= 3:
                        sessions.add(parts[1])
            except Exception:
                self._use_redis = False
        # include in-memory sessions
        for k in list(self._in_memory.keys()):
            if k == "_last":
                continue
            sessions.add(k)
        return list(sessions)

    async def get_last_seen(self, session_id: str) -> float:
        if self._use_redis:
            try:
                v = await self._r.get(f"session:{session_id}:last")
                if v:
                    return json.loads(v).get("ts", 0.0)
            except Exception:
                self._use_redis = False
        return self._in_memory.get("_last", {}).get(session_id, 0.0)

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

    async def mark_finalized(self, session_id: str):
        if self._use_redis:
            try:
                await self._r.set(f"session:{session_id}:finalized", "1")
                return
            except Exception:
                self._use_redis = False
        self._in_memory_extracted.setdefault(session_id, {})
        self._in_memory_extracted[session_id]["_finalized"] = True

    async def is_finalized(self, session_id: str) -> bool:
        if self._use_redis:
            try:
                v = await self._r.get(f"session:{session_id}:finalized")
                return bool(v)
            except Exception:
                self._use_redis = False
        return bool(self._in_memory_extracted.get(session_id, {}).get("_finalized", False))

    async def get_extracted(self, session_id: str) -> Dict[str, Any]:
        key = f"session:{session_id}:extracted"
        if self._use_redis:
            try:
                v = await self._r.get(key)
                return json.loads(v) if v else {}
            except Exception:
                self._use_redis = False
        return self._in_memory_extracted.get(session_id, {})
