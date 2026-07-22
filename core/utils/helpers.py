import uuid
import hashlib
import json
import asyncio
from datetime import datetime
from typing import Any, List, TypeVar, Callable, Awaitable
from functools import wraps
import time

T = TypeVar('T')

def generate_id() -> str:
    """Generate a UUID4 string."""
    return str(uuid.uuid4())

def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.utcnow()

def hash_value(value: str) -> str:
    """Hash a string using SHA256."""
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def safe_json_loads(data: str, default: Any = None) -> Any:
    """Safely parse JSON with fallback."""
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default if default is not None else {}

def safe_json_dumps(data: Any) -> str:
    """Safely serialize to JSON handling datetimes."""
    def default_serializer(obj: Any) -> str:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)
    
    return json.dumps(data, default=default_serializer)

def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """Split a list into chunks."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def retry_async(retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry an async function."""
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            current_delay = delay
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries - 1:
                        raise e
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            raise Exception("Retry failed")
        return wrapper
    return decorator

class Timer:
    """Context manager for performance measurement."""
    def __init__(self, name: str, logger: Any = None):
        self.name = name
        self.logger = logger
        self.start_time = 0.0

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        elapsed = time.perf_counter() - self.start_time
        if self.logger:
            self.logger.info(f"{self.name} took {elapsed:.4f}s")
        else:
            print(f"{self.name} took {elapsed:.4f}s")
