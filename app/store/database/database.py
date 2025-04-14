from dataclasses import dataclass
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, MetaData
from app.store.database.sqlalchemy_base import Base
import logging

@dataclass
class Database:

    def __init__(self, app = None):
        self.app = app
        self.engine = None 
        self.session_factory = None
        self.logger = logging.getLogger("database")
        self.Base = Base
        self.metadata = Base.metadata
        self._db = type('DBProxy', (), {'metadata': self.metadata})

    async def connect(self, *args, **kwargs):
        db_url = self.app.config.database.url 
        self.engine = create_async_engine(db_url, echo = True)
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    
        async with self.engine.begin() as conn:
            await conn.run_sync(self.metadata.create_all)

        async with self.session() as session:
            await session.execute(text("SELECT 1"))
            self.logger.info("Database connection established")
        

    async def disconnect(self, *args, **kwargs):
        if self.engine:
            await self.engine.dispose()
            self.logger.info("Database connection closed")
   

    def session(self):
        if not self.session_factory:
            raise RuntimeError("Database is not connected")
        return self.session_factory()