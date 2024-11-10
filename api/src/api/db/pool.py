import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, sessionmaker

from api.db.models import Base, Workflow

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+asyncpg://postgres:password@db:5432/postgres"
)

# create vectordb connectionstring
VECTOR_DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycog2://postgres:password@db:5432/vectordb"
)

# Create an asynchronous engine
# Create an asynchronous engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Enable SQL echo for debugging (can be set to False in production)
    future=True,  # Use SQLAlchemy 2.0 style
    pool_size=100,  # Adjust the pool size according to your workload
    max_overflow=20,  # Extra connections allowed to "overflow" the pool
    pool_timeout=30,  # Timeout before the pool raises an error
    pool_recycle=3600,  # Recycle connections after an hour
)

# Create a session factory
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Dependency for getting a DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


async def create_sample_data():
    async with AsyncSessionLocal() as session:  # New session for sample data
        async with session.begin():  # Transaction management
            # check if there are any users in the db
            # delete all users from table
            # create python Workflow
            # check if workflow exists with name python
            result = await session.execute(
                select(Workflow).filter(Workflow.name == "python")
            )
            workflow_exists = result.scalars().first()
            if not workflow_exists:
                workflow = Workflow(name="python", description="A Python workflow")
                session.add(workflow)

            # # execute CREATE EXTENSION IF NOT EXISTS vector;
            # await session.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))

            await session.commit()  # Commit the transaction


# Optional: Function to initialize the database connection
async def init_db():

    async with engine.begin() as conn:
        # await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        # await conn.execute(text("CREATE SCHEMA public"))
        await conn.run_sync(Base.metadata.create_all)

    # Create sample data
    await create_sample_data()
