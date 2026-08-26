from fastapi import APIRouter, Depends, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.budget_access import get_budget_for_member
from app.currency import convert_amount
from app.database import get_db
from app.models import Budget, Transaction, TransactionType, User
from app.schemas import BudgetOut, TransactionCreate, TransactionOut

router = APIRouter(prefix="/budgets/{budget_id}/transactions", tags=["transactions"])


@router.post("/", response_model=TransactionOut, status_code=status.HTTP_201_CREATED)
async def add_transaction(
    budget_id: int,
    payload: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TransactionOut:
    budget = await get_budget_for_member(budget_id, current_user, db)

    converted = await convert_amount(payload.original_amount, payload.original_currency, budget.base_currency)
    signed_amount = -converted if payload.type == TransactionType.withdrawal else converted

    transaction = Transaction(
        budget_id=budget_id,
        user_id=current_user.id,
        original_amount=payload.original_amount,
        original_currency=payload.original_currency,
        converted_amount=signed_amount,
        type=payload.type,
        note=payload.note,
    )
    db.add(transaction)

    await db.execute(
        update(Budget)
        .where(Budget.id == budget_id)
        .values(current_amount=Budget.current_amount + signed_amount)
    )

    await db.commit()
    await db.refresh(transaction)
    await db.refresh(budget)

    return TransactionOut(
        id=transaction.id,
        budget_id=transaction.budget_id,
        user_id=transaction.user_id,
        username=current_user.username,
        original_amount=transaction.original_amount,
        original_currency=transaction.original_currency,
        converted_amount=transaction.converted_amount,
        type=transaction.type,
        note=transaction.note,
        created_at=transaction.created_at,
        budget=BudgetOut.model_validate(budget),
    )


@router.get("/", response_model=list[TransactionOut])
async def list_transactions(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TransactionOut]:
    budget = await get_budget_for_member(budget_id, current_user, db)

    result = await db.execute(
        select(Transaction, User.username)
        .join(User, User.id == Transaction.user_id)
        .where(Transaction.budget_id == budget_id)
        .order_by(Transaction.created_at.desc())
    )
    budget_out = BudgetOut.model_validate(budget)

    return [
        TransactionOut(
            id=t.id,
            budget_id=t.budget_id,
            user_id=t.user_id,
            username=username,
            original_amount=t.original_amount,
            original_currency=t.original_currency,
            converted_amount=t.converted_amount,
            type=t.type,
            note=t.note,
            created_at=t.created_at,
            budget=budget_out,
        )
        for t, username in result.all()
    ]
