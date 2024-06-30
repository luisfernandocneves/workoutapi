from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker




engine = create_async_engine('postgresql+asyncpg://workout:workout@localhost/workout', echo=False)
assync_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncGenerator:
    async with assync_session() as session:
        yield session