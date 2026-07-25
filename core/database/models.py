from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Index, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from core.schemas.investigation import CaseStatus
from core.schemas.transaction import TransactionStatus, TransactionType


def utc_now():
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TransactionRecord(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    type: Mapped[TransactionType] = mapped_column(SQLEnum(TransactionType))
    amount: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    sender_id: Mapped[str] = mapped_column(String, index=True)
    receiver_id: Mapped[str] = mapped_column(String, index=True)
    status: Mapped[TransactionStatus] = mapped_column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    __table_args__ = (
        Index('idx_txn_timestamp', 'timestamp'),
    )


class UserRecord(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class MerchantRecord(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    mcc_code: Mapped[str] = mapped_column(String)


class DeviceRecord(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    device_type: Mapped[str] = mapped_column(String)


class AlertRecord(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String, ForeignKey("transactions.id"))
    risk_score: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class InvestigationCaseRecord(Base):
    __tablename__ = "investigation_cases"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[CaseStatus] = mapped_column(SQLEnum(CaseStatus))
    assigned_to: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class AuditLogRecord(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String)
    action: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utc_now)


class EventStoreRecord(Base):
    __tablename__ = "event_store"

    sequence_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    aggregate_id: Mapped[str] = mapped_column(String, index=True)
    event_type: Mapped[str] = mapped_column(String, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=utc_now)
    payload_json: Mapped[dict] = mapped_column(JSON)
    agent_name: Mapped[str] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index('idx_aggregate_time', 'aggregate_id', 'timestamp'),
    )
