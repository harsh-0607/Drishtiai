from __future__ import annotations

import os

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


def get_mongo_client() -> AsyncIOMotorClient:
    """Create a Motor client from MONGODB_URI."""

    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    return AsyncIOMotorClient(uri)


def get_mongo_db() -> AsyncIOMotorDatabase:
    """Get the MongoDB database used by DRISHTI."""

    db_name = os.getenv("MONGODB_DB", "drishti")
    return get_mongo_client()[db_name]
