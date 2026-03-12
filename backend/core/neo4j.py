from typing import Optional, List, Dict, Any
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession, Transaction
from neo4j.exceptions import ServiceUnavailable, AuthError

from backend.core.config import settings
from backend.core.logging import logger


class Neo4jConnection:
    _instance: Optional["Neo4jConnection"] = None
    _driver: Optional[AsyncDriver] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        if self._driver is None:
            try:
                self._driver = AsyncGraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                    max_connection_lifetime=3600,
                    max_connection_pool_size=50,
                    connection_acquisition_timeout=60,
                )
                await self._driver.verify_connectivity()
                logger.info("Connected to Neo4j successfully")
            except AuthError as e:
                logger.error(f"Neo4j authentication failed: {e}")
                raise
            except ServiceUnavailable as e:
                logger.error(f"Neo4j service unavailable: {e}")
                raise

    async def close(self) -> None:
        if self._driver:
            await self._driver.close()
            self._driver = None
            logger.info("Neo4j connection closed")

    async def get_session(self) -> AsyncSession:
        if self._driver is None:
            await self.connect()
        return self._driver.session()

    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        async with await self.get_session() as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    async def execute_write(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        async with await self.get_session() as session:
            result = await session.run(query, parameters or {})
            await result.consume()
            return []


neo4j_connection = Neo4jConnection()


async def get_neo4j_session() -> AsyncSession:
    return await neo4j_connection.get_session()
