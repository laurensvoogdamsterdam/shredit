from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from api.db.models import User, Base, UserRole

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@db:5432/postgres")

# Create an asynchronous engine
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

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
            result = await session.execute(User.__table__.select())
            users = result.scalars().all()
            if len(users) == 0:
                

                session.add_all(
                    [
                        User(
                            auth0_id="auth0|1",
                            username="athlete1",
                            email="athlete1@example.com",
                            full_name="Athlete One",
                            role=UserRole.ATHLETE
                        ),
                        User(
                            auth0_id="auth0|2",
                            username="trainer1",
                            email="trainer1@example.com",
                            full_name="Trainer One",
                            role=UserRole.TRAINER
                        ),
                        User(
                            auth0_id="auth0|3",
                            username="coach1",
                            email="coach1@example.com",
                            full_name="Coach One",
                            role=UserRole.COACH
                        ),
                        User(
                            auth0_id="auth0|4",
                            username="dietician1",
                            email="dietician1@example.com",
                            full_name="Dietician One",
                            role=UserRole.DIETICIAN
                        ),
                        User(
                            auth0_id="auth0|5",
                            username="athlete2",
                            email="athlete2@example.com",
                            full_name="Athlete Two",
                            role=UserRole.ATHLETE
                        ),
                    ]
                )
            await session.commit()  # Commit the transaction


# Optional: Function to initialize the database connection
async def init_db():
    async with engine.begin() as conn:
        # Create all tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)

    # Create sample data
    await create_sample_data()
