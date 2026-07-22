from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    postgres_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/aegis"
    sqlite_fallback: str = "sqlite+aiosqlite:///./aegis.db"
    
    model_config = SettingsConfigDict(env_prefix="AEGIS_DB_", env_file=".env", extra="ignore")


class RedisSettings(BaseSettings):
    url: str = "redis://localhost:6379/0"
    host: str = "localhost"
    port: int = 6379
    
    model_config = SettingsConfigDict(env_prefix="AEGIS_REDIS_", env_file=".env", extra="ignore")


class KafkaSettings(BaseSettings):
    bootstrap_servers: str = "localhost:9092"
    topics: str = "transactions,alerts,investigations"
    
    model_config = SettingsConfigDict(env_prefix="AEGIS_KAFKA_", env_file=".env", extra="ignore")


class Neo4jSettings(BaseSettings):
    uri: str = "bolt://localhost:7687"
    user: str = "neo4j"
    password: str = "password"
    
    model_config = SettingsConfigDict(env_prefix="AEGIS_NEO4J_", env_file=".env", extra="ignore")


class QdrantSettings(BaseSettings):
    url: str = "http://localhost:6333"
    collection: str = "aegis_entities"
    
    model_config = SettingsConfigDict(env_prefix="AEGIS_QDRANT_", env_file=".env", extra="ignore")


class MinioSettings(BaseSettings):
    endpoint: str = "localhost:9000"
    access_key: str = "minioadmin"
    secret_key: str = "minioadmin"
    
    model_config = SettingsConfigDict(env_prefix="AEGIS_MINIO_", env_file=".env", extra="ignore")


class SecuritySettings(BaseSettings):
    secret_key: str = "super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire: int = 3600
    
    model_config = SettingsConfigDict(env_prefix="AEGIS_SECURITY_", env_file=".env", extra="ignore")


class LLMSettings(BaseSettings):
    provider: str = "openai"
    api_key: Optional[str] = None
    model: str = "gpt-4-turbo"
    
    model_config = SettingsConfigDict(env_prefix="AEGIS_LLM_", env_file=".env", extra="ignore")


class FeatureFlagsSettings(BaseSettings):
    enable_graph: bool = True
    enable_agents: bool = True
    enable_streaming: bool = False
    
    model_config = SettingsConfigDict(env_prefix="AEGIS_FEATURE_", env_file=".env", extra="ignore")


class AegisSettings(BaseSettings):
    db: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    kafka: KafkaSettings = KafkaSettings()
    neo4j: Neo4jSettings = Neo4jSettings()
    qdrant: QdrantSettings = QdrantSettings()
    minio: MinioSettings = MinioSettings()
    security: SecuritySettings = SecuritySettings()
    llm: LLMSettings = LLMSettings()
    features: FeatureFlagsSettings = FeatureFlagsSettings()
    
    model_config = SettingsConfigDict(env_prefix="AEGIS_", env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> AegisSettings:
    return AegisSettings()
