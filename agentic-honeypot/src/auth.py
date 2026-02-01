import os
import time
import threading
from typing import List

# Load initial keys from environment. We support dynamic reload by
# re-reading the env var when `check_api_key` is called and updating the
# in-memory set when it changes.
API_KEY_ENV = os.getenv("API_KEYS", os.getenv("API_KEY", "secret-key"))
_cached_env_str = API_KEY_ENV
LOCAL_KEYS = set(k.strip() for k in API_KEY_ENV.split(",") if k.strip())
RATE_LIMIT = int(os.getenv("RATE_LIMIT_PER_MIN", "60"))
REDIS_URL = os.getenv("REDIS_URL")

# lock protecting LOCAL_KEYS/_cached_env_str updates
_keys_lock = threading.Lock()

try:
    import redis
    redis_sync = redis.from_url(REDIS_URL) if REDIS_URL else None
except Exception:
    redis_sync = None


def _populate_redis_keys(keys=None):
    if redis_sync is None:
        return
    try:
        target = keys if keys is not None else LOCAL_KEYS
        for k in target:
            redis_sync.sadd("api_keys", k)
    except Exception:
        pass


def check_api_key(key: str) -> bool:
    if not key:
        return False
    # refresh keys from env if changed
    try:
        env_now = os.getenv("API_KEYS", os.getenv("API_KEY", "secret-key"))
        global _cached_env_str
        if env_now != _cached_env_str:
            with _keys_lock:
                # re-check inside lock
                if env_now != _cached_env_str:
                    _cached_env_str = env_now
                    new_keys = set(k.strip() for k in env_now.split(",") if k.strip())
                    LOCAL_KEYS.clear()
                    LOCAL_KEYS.update(new_keys)
                    # propagate to redis if present
                    _populate_redis_keys(new_keys)
    except Exception:
        pass

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


def set_api_keys(keys: List[str]) -> bool:
    """Replace in-memory API key set with `keys` and propagate to redis.

    This updates the process-local `LOCAL_KEYS`, updates the cached env
    string, writes to `os.environ["API_KEYS"]` (so other tooling can read it),
    and populates Redis if available. Returns True on success.
    """
    try:
        new_set = set(k.strip() for k in keys if k and k.strip())
        with _keys_lock:
            LOCAL_KEYS.clear()
            LOCAL_KEYS.update(new_set)
            global _cached_env_str
            _cached_env_str = ",".join(sorted(new_set))
            # update env for visibility (process-level only)
            os.environ["API_KEYS"] = _cached_env_str
            # push to redis
            _populate_redis_keys(new_set)
        return True
    except Exception:
        return False
