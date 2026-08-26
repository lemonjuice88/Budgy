from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field, field_validator, model_validator

from app.models import TransactionType


class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    username: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class BudgetCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    target_amount: float = Field(gt=0)
    base_currency: str = Field(min_length=3, max_length=3)

    @field_validator("base_currency")
    @classmethod
    def uppercase_currency(cls, v: str) -> str:
        return v.upper()


class BudgetUpdate(BaseModel):
    is_completed: bool


class BudgetJoin(BaseModel):
    budget_id: int | None = None
    invite_code: str | None = None

    @model_validator(mode="after")
    def require_one_identifier(self) -> "BudgetJoin":
        if not self.budget_id and not self.invite_code:
            raise ValueError("budget_id veya invite_code alanlarından biri zorunludur")
        return self


class BudgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    target_amount: float
    current_amount: float
    base_currency: str
    is_completed: bool
    invite_code: str
    created_by: int
    created_at: datetime

    @computed_field
    @property
    def percentage(self) -> float:
        if self.target_amount <= 0:
            return 0.0
        return round((self.current_amount / self.target_amount) * 100, 2)


class TransactionCreate(BaseModel):
    original_amount: float = Field(gt=0)
    original_currency: str = Field(min_length=3, max_length=3)
    type: TransactionType = TransactionType.deposit
    note: str | None = Field(default=None, max_length=255)

    @field_validator("original_currency")
    @classmethod
    def uppercase_currency(cls, v: str) -> str:
        return v.upper()


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    budget_id: int
    user_id: int
    username: str
    original_amount: float
    original_currency: str
    converted_amount: float
    type: TransactionType
    note: str | None
    created_at: datetime
    budget: BudgetOut
