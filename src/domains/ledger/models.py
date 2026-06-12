import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    UniqueConstraint,
)

from src.core.database import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String, nullable=False, index=True)
    balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    currency = Column(String(3), default="USD", nullable=False)

    # FIX: Explicitly set timezone=True
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (CheckConstraint("balance >= 0", name="check_positive_balance"),)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    idempotency_key = Column(String, unique=True, nullable=False, index=True)

    from_account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    to_account_id = Column(String, ForeignKey("accounts.id"), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)

    status = Column(String, default="PENDING", nullable=False)

    # FIX: Explicitly set timezone=True
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_idempotency_key"),
        CheckConstraint("amount > 0", name="check_positive_amount"),
    )
