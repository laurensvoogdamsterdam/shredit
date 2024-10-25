import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from api.db.models import Base, User, UserRole

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@db:5432/postgres")

# Create an asynchronous engine
# Create an asynchronous engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Enable SQL echo for debugging (can be set to False in production)
    future=True,  # Use SQLAlchemy 2.0 style
    pool_size=100,  # Adjust the pool size according to your workload
    max_overflow=20,  # Extra connections allowed to "overflow" the pool
    pool_timeout=30,  # Timeout before the pool raises an error
    pool_recycle=3600  # Recycle connections after an hour
)

# Create a session factory
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Dependency for getting a DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

async def create_sample_data():
    async with AsyncSessionLocal() as session:  # New session for sample data
        async with session.begin():  # Transaction management
            # check if there are any users in the db
            # delete all users from table
            # await session.execute(User.__table__.delete())
            
            await session.commit()  # Commit the transaction


# Optional: Function to initialize the database connection
async def init_db():
    async with engine.begin() as conn:
        # Create all tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

    # Create sample data
    await create_sample_data()


