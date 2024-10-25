import graphene
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import User
from api.db.pool import AsyncSessionLocal


# Define User GraphQL Type
class UserType(graphene.ObjectType):
    id = graphene.Int()
    auth0_id = graphene.String()
    username = graphene.String()
    email = graphene.String()
    full_name = graphene.String()


class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    user_by_id = graphene.Field(UserType, id=graphene.Int(required=True))

    async def resolve_users(self, info):
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User))
            return result.scalars().all()

    async def resolve_user_by_id(self, info, id):        
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).filter(User.id == id))
            return result.scalar_one_or_none()

# Define the schema with the UserType and Query
schema = graphene.Schema(query=Query)
