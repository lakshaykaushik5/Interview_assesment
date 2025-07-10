import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.future import select
from contextlib import asynccontextmanager
from .models import Base, MasterDocs
import os
from dotenv import load_dotenv, find_dotenv
# from env import port,postgres_password,postgres_user,host,db_name


load_dotenv(find_dotenv())

postgres_user=os.getenv("POSTGRES_USER")
postgres_password=os.getenv("POSTGRES_PASSWORD")
host = os.getenv("HOST")
db_name=os.getenv("POSTGRES_DB")
port=os.getenv("PORT")

print(postgres_password," ||| ",postgres_user," ||| ",host," ||| ",db_name," ||| ",port," --------------")
DATABASE_URL = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{host}:{port}/{db_name}"

print(DATABASE_URL,'======||+++++++++++++++++++++++++')

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


async def drip_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    print("Database tables dropped")
    


