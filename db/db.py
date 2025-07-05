import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select
from contextlib import asynccontextmanager
from .models import Base, MasterDocs

postgres_user=""
postgres_password=""
host = ""
db_name=""
port=""

DATABASE_URL = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{host}:{port}/{db_name}"

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            print("Error in DB :: ",e)
            await session.rollback()
            raise
        finally:
            await session.close()
            

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database initialized")