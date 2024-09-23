from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://username:password@localhost/dbname")  # Update with your DB credentials

# Create an asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# Create a session factory
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Dependency for getting a DB session
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session

# Optional: Function to initialize the database connection
async def init_db():
    async with engine.begin() as conn:
        # Create all tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
