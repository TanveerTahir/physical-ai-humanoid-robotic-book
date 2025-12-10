"""
Database connection setup for the Physical AI & Humanoid Robotics textbook platform.
This module handles database connections for both SQL and vector databases.
"""
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.pool import QueuePool


class DatabaseManager:
    """
    Database manager for handling connections to various databases used in the platform.
    """

    def __init__(self):
        # SQL Database configuration
        self.sql_database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://username:password@localhost/dbname")

        # Initialize engines
        self.sql_engine = create_async_engine(
            self.sql_database_url,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=300,
        )

        # Create async session maker
        self.async_session = async_sessionmaker(
            self.sql_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get an async database session.
        """
        async with self.async_session() as session:
            try:
                yield session
            finally:
                await session.close()

    async def close_connections(self):
        """
        Close all database connections.
        """
        await self.sql_engine.dispose()


# Create a global database manager instance
db_manager = DatabaseManager()


# Convenience function to get database session
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Convenience function to get database session for dependency injection.
    """
    async with db_manager.async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Qdrant client setup
from qdrant_client import AsyncQdrantClient


class VectorDBManager:
    """
    Vector database manager for handling Qdrant connections.
    """

    def __init__(self):
        self.qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self.qdrant_client = AsyncQdrantClient(url=self.qdrant_url)

    def get_client(self):
        """
        Get the Qdrant client instance.
        """
        return self.qdrant_client

    async def close_connections(self):
        """
        Close Qdrant connections.
        """
        await self.qdrant_client.aclose()


# Create a global vector database manager instance
vector_db_manager = VectorDBManager()


# Convenience function to get Qdrant client
def get_vector_db_client():
    """
    Convenience function to get Qdrant client for dependency injection.
    """
    return vector_db_manager.get_client()