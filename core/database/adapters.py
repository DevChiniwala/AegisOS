from typing import Protocol, Any, List, Optional
from core.config.settings import DatabaseSettings


class DatabaseAdapter(Protocol):
    async def connect(self) -> None:
        ...

    async def disconnect(self) -> None:
        ...

    async def execute(self, query: str, *args: Any, **kwargs: Any) -> Any:
        ...

    async def fetch_one(self, query: str, *args: Any, **kwargs: Any) -> Optional[Any]:
        ...

    async def fetch_all(self, query: str, *args: Any, **kwargs: Any) -> List[Any]:
        ...

    async def health_check(self) -> bool:
        ...


class SQLiteAdapter:
    def __init__(self, dsn: str):
        self.dsn = dsn

    async def connect(self) -> None:
        # Implementation for aiosqlite
        pass

    async def disconnect(self) -> None:
        pass

    async def execute(self, query: str, *args: Any, **kwargs: Any) -> Any:
        pass

    async def fetch_one(self, query: str, *args: Any, **kwargs: Any) -> Optional[Any]:
        return None

    async def fetch_all(self, query: str, *args: Any, **kwargs: Any) -> List[Any]:
        return []

    async def health_check(self) -> bool:
        return True


class PostgreSQLAdapter:
    def __init__(self, dsn: str):
        self.dsn = dsn

    async def connect(self) -> None:
        # Implementation for asyncpg
        pass

    async def disconnect(self) -> None:
        pass

    async def execute(self, query: str, *args: Any, **kwargs: Any) -> Any:
        pass

    async def fetch_one(self, query: str, *args: Any, **kwargs: Any) -> Optional[Any]:
        return None

    async def fetch_all(self, query: str, *args: Any, **kwargs: Any) -> List[Any]:
        return []

    async def health_check(self) -> bool:
        return True


def get_database_adapter(settings: DatabaseSettings) -> DatabaseAdapter:
    # A real implementation would pick the adapter based on settings
    if settings.postgres_url:
        return PostgreSQLAdapter(settings.postgres_url)
    return SQLiteAdapter(settings.sqlite_fallback)
