"""Verify the SQLAlchemy models match the live Supabase schema.

Run from the backend/ directory:  python -m scripts.check_db
"""

import asyncio

from sqlalchemy import func, select

from app.core.db import SessionLocal, engine
from app.models import (
    Opportunity,
    OpportunityMatch,
    Profile,
    ProfileInterest,
    ProfileSkill,
    User,
    UserOpportunityAction,
)

MODELS = [
    User,
    Profile,
    ProfileSkill,
    ProfileInterest,
    Opportunity,
    OpportunityMatch,
    UserOpportunityAction,
]


async def main() -> None:
    async with SessionLocal() as session:
        for model in MODELS:
            count = await session.scalar(select(func.count()).select_from(model))
            print(f"  {model.__tablename__:<28} {count:>5} rows")

        # Loading a full row proves every mapped column exists with a compatible type,
        # which counting alone does not.
        opportunity = await session.scalar(select(Opportunity).limit(1))
        if opportunity is None:
            print("\nNo opportunities seeded yet (expected until Sprint 3).")
        else:
            print(
                f"\nSample opportunity: {opportunity.title!r} "
                f"({opportunity.category}, deadline={opportunity.deadline})"
            )

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
