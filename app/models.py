import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TransactionType(str, enum.Enum):
    deposit = "deposit"
    withdrawal = "withdrawal"
    saving = "saving"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    owned_budgets: Mapped[list["Budget"]] = relationship(
        back_populates="owner", foreign_keys="Budget.created_by"
    )
    memberships: Mapped[list["BudgetMember"]] = relationship(back_populates="user")


class Budget(Base):
    __tablename__ = "budgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    target_amount: Mapped[float] = mapped_column(Numeric(12, 2, asdecimal=False), nullable=False)
    current_amount: Mapped[float] = mapped_column(
        Numeric(12, 2, asdecimal=False), nullable=False, default=0
    )

    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="TRY")

    is_completed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    invite_code: Mapped[str] = mapped_column(
        String(32), unique=True, index=True, default=lambda: uuid.uuid4().hex
    )

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    owner: Mapped["User"] = relationship(back_populates="owned_budgets", foreign_keys=[created_by])
    members: Mapped[list["BudgetMember"]] = relationship(
        back_populates="budget", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="budget", cascade="all, delete-orphan"
    )


class BudgetMember(Base):
    __tablename__ = "budget_members"
    __table_args__ = (UniqueConstraint("budget_id", "user_id", name="uq_budget_member"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    budget_id: Mapped[int] = mapped_column(ForeignKey("budgets.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    budget: Mapped["Budget"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    budget_id: Mapped[int] = mapped_column(ForeignKey("budgets.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    original_amount: Mapped[float] = mapped_column(Numeric(12, 2, asdecimal=False), nullable=False)
    original_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    converted_amount: Mapped[float] = mapped_column(Numeric(12, 2, asdecimal=False), nullable=False)

    type: Mapped[TransactionType] = mapped_column(
        Enum(TransactionType, name="transaction_type"), nullable=False, default=TransactionType.deposit
    )
    note: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    budget: Mapped["Budget"] = relationship(back_populates="transactions")
    user: Mapped["User"] = relationship()
