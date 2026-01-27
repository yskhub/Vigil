import os
import time
from typing import List

API_KEY_ENV = os.getenv("API_KEYS", os.getenv("API_KEY", "secret-key"))
LOCAL_KEYS = set(k.strip() for k in API_KEY_ENV.split(",") if k.strip())
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))
REDIS_URL = os.getenv("REDIS_URL")

try:
    import redis
    redis_sync = redis.from_url(REDIS_URL) if REDIS_URL else None
except Exception:
    redis_sync = None


def _populate_redis_keys():
    if redis_sync is None:
        return
    try:
        for k in LOCAL_KEYS:
            redis_sync.sadd("api_keys", k)
    except Exception:
        pass


def check_api_key(key: str) -> bool:
    if not key:
        return False
    if redis_sync is not None:
        try:
            if redis_sync.sismember("api_keys", key):
                return True
        except Exception:
            pass
    return key in LOCAL_KEYS


def rate_limit_ok(key: str) -> bool:
    now = int(time.time())
    window = now // 60
    if redis_sync is not None:
        try:
            kname = f"rate:{key}:{window}"
            val = redis_sync.incr(kname)
            if val == 1:
                redis_sync.expire(kname, 65)
            return val <= RATE_LIMIT
        except Exception:
            pass
    # fallback in-memory
    # simple global memory store
    global _mem_rate
    try:
        _mem_rate
    except NameError:
        _mem_rate = {}
    st = _mem_rate.setdefault(key, {})
    if st.get("window") != window:
        st["window"] = window
        st["count"] = 0
    if st["count"] >= RATE_LIMIT:
        return False
    st["count"] += 1
    return True


# populate keys into redis if available
_populate_redis_keys()
