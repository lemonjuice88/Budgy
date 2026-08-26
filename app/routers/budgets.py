from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.budget_access import get_budget_for_member, require_owner
from app.database import get_db
from app.models import Budget, BudgetMember, User
from app.schemas import BudgetCreate, BudgetJoin, BudgetOut, BudgetUpdate

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.post("/", response_model=BudgetOut, status_code=status.HTTP_201_CREATED)
async def create_budget(
    payload: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Budget:
    budget = Budget(
        title=payload.title,
        target_amount=payload.target_amount,
        current_amount=0,
        base_currency=payload.base_currency,
        created_by=current_user.id,
    )
    db.add(budget)
    await db.flush()

    db.add(BudgetMember(budget_id=budget.id, user_id=current_user.id))
    await db.commit()
    await db.refresh(budget)
    return budget


@router.get("/", response_model=list[BudgetOut])
async def list_my_budgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Budget]:
    result = await db.execute(
        select(Budget)
        .join(BudgetMember, BudgetMember.budget_id == Budget.id)
        .where(BudgetMember.user_id == current_user.id, Budget.is_completed == False)
        .order_by(Budget.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/completed", response_model=list[BudgetOut])
async def list_completed_budgets(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[Budget]:
    result = await db.execute(
        select(Budget)
        .join(BudgetMember, BudgetMember.budget_id == Budget.id)
        .where(BudgetMember.user_id == current_user.id, Budget.is_completed == True)
        .order_by(Budget.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{budget_id}", response_model=BudgetOut)
async def get_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Budget:
    return await get_budget_for_member(budget_id, current_user, db)


@router.patch("/{budget_id}", response_model=BudgetOut)
async def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Budget:
    budget = await get_budget_for_member(budget_id, current_user, db)
    require_owner(budget, current_user)

    budget.is_completed = payload.is_completed
    await db.commit()
    await db.refresh(budget)
    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    budget = await get_budget_for_member(budget_id, current_user, db)
    require_owner(budget, current_user)

    await db.delete(budget)
    await db.commit()


@router.post("/join", response_model=BudgetOut)
async def join_budget(
    payload: BudgetJoin,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Budget:
    conditions = []
    if payload.budget_id is not None:
        conditions.append(Budget.id == payload.budget_id)
    if payload.invite_code is not None:
        conditions.append(Budget.invite_code == payload.invite_code)

    result = await db.execute(select(Budget).where(or_(*conditions)))
    budget = result.scalar_one_or_none()
    if budget is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Bütçe bulunamadı")

    existing = await db.execute(
        select(BudgetMember).where(
            BudgetMember.budget_id == budget.id,
            BudgetMember.user_id == current_user.id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Bu bütçeye zaten üyesiniz")

    db.add(BudgetMember(budget_id=budget.id, user_id=current_user.id))
    await db.commit()
    await db.refresh(budget)
    return budget
