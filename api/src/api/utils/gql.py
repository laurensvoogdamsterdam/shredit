import strawberry
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.db.models import User, TrainingPlan, DietaryPlan, UserRole, DietaryPlanType, TrainingPlanType
from enum import Enum
from typing import Any, List

async def get_training_plans_for_user(user: User, info) -> list[TrainingPlanType]:
    return await get_training_plans(user.id, info)

# Enum for Training Plan Type
class TrainingPlanTypeEnum(Enum):
    STRENGTH = "STRENGTH"
    ENDURANCE = "ENDURANCE"
    FLEXIBILITY = "FLEXIBILITY"

TrainingPlanTypeEnum = strawberry.enum(TrainingPlanTypeEnum)

# Enum for Dietary Plan Type
class DietaryPlanTypeEnum(Enum):
    WEIGHT_LOSS = "WEIGHT_LOSS"
    WEIGHT_GAIN = "WEIGHT_GAIN"
    MUSCLE_GAIN = "MUSCLE_GAIN"
    MAINTENANCE = "MAINTENANCE"

DietaryPlanTypeEnum = strawberry.enum(DietaryPlanTypeEnum)


@strawberry.type
class UserType:
    id: int
    username: str
    email: str
    full_name: str
    training_plans: list['TrainingPlan'] = strawberry.field(resolver=get_training_plans_for_user)

async def get_training_plans_for_user(user: UserType, info) -> list[TrainingPlanType]:
    return await get_training_plans(user.id, info)

async def get_training_plans(user_id: int, info) -> list[TrainingPlanType]:
    async with info.context['session']() as session:
        result = await session.execute(select(TrainingPlan).where(TrainingPlan.user_id == user_id))
        return result.scalars().all()


async def get_users_subscribed_to_plan(plan_id: int, info) -> list[UserType]:
    async with info.context['session']() as session:
        result = await session.execute(
            select(User).join(TrainingPlan.subscribers).where(TrainingPlan.id == plan_id)
        )
        return result.scalars().all()

# make TrainingPlanType into strawberry.type
class TrainingPlanTypeEnum(Enum):
    STRENGTH = "STRENGTH"
    ENDURANCE = "ENDURANCE"
    FLEXIBILITY = "FLEXIBILITY"

# Create a Strawberry enum from the Python Enum
TrainingPlanTypeEnum = strawberry.enum(TrainingPlanTypeEnum)


# Define TrainingPlan using the enum
@strawberry.type
class TrainingPlan:
    id: int
    user_id: int
    name: str
    description: str
    type: TrainingPlanTypeEnum  
    subscribers: list[UserType] = strawberry.field(resolver=get_users_subscribed_to_plan)

# Define DietaryPlan using the enum
@strawberry.type
class DietaryPlan:
    id: int
    user_id: int
    name: str
    description: str
    type: DietaryPlanTypeEnum

async def get_training_plans(user_id: int, info) -> list[TrainingPlanType]:
    async with info.context['session']() as session:
        result = await session.execute(select(TrainingPlan).where(TrainingPlan.user_id == user_id))
        return result.scalars().all()


async def get_users_subscribed_to_plan(plan_id: int, info) -> list[UserType]:
    async with info.context['session']() as session:
        result = await session.execute(
            select(User).join(TrainingPlan.subscribers).where(TrainingPlan.id == plan_id)
        )
        return result.scalars().all()


@strawberry.type
class Query:
    @strawberry.field
    async def users(self, info) -> list[UserType]:
        async with info.context['session']() as session:
            result = await session.execute(select(User))
            return result.scalars().all()

    @strawberry.field
    async def training_plans(self, info) -> list[TrainingPlanType]:
        async with info.context['session']() as session:
            result = await session.execute(select(TrainingPlan))
            return result.scalars().all()

    @strawberry.field
    async def dietary_plans(self, info) -> list[DietaryPlanType]:
        async with info.context['session']() as session:
            result = await session.execute(select(DietaryPlan))
            return result.scalars().all()

    @strawberry.field
    async def user_by_id(self, id: int, info) -> UserType:
        async with info.context['session']() as session:
            result = await session.execute(select(User).where(User.id == id))
            return result.scalar_one_or_none()

    @strawberry.field
    async def training_plan_by_id(self, id: int, info) -> TrainingPlanType:
        async with info.context['session']() as session:
            result = await session.execute(select(TrainingPlan).where(TrainingPlan.id == id))
            return result.scalar_one_or_none()

    @strawberry.field
    async def dietary_plan_by_id(self, id: int, info) -> DietaryPlanType:
        async with info.context['session']() as session:
            result = await session.execute(select(DietaryPlan).where(DietaryPlan.id == id))
            return result.scalar_one_or_none()


schema = strawberry.Schema(query=Query)
