from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Budget, BudgetMember, User


async def get_budget_for_member(budget_id: int, current_user: User, db: AsyncSession) -> Budget:
    budget = await db.get(Budget, budget_id)
    if budget is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bütçe bulunamadı")

    membership = await db.execute(
        select(BudgetMember).where(
            BudgetMember.budget_id == budget_id,
            BudgetMember.user_id == current_user.id,
        )
    )
    if membership.scalar_one_or_none() is None:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Bu bütçenin üyesi değilsiniz")

    return budget


def require_owner(budget: Budget, current_user: User) -> None:
    if budget.created_by != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Bu işlem için bütçe sahibi olmanız gerekir")
