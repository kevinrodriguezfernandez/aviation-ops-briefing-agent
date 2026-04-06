"""Minimal smoke tests for src/db models and connection."""

import os

import pytest
from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.config import get_settings
from src.db.models import Airport, Base, Flight, Notam, Sop

DATABASE_URL = os.environ["DATABASE_URL"]
EMBEDDING_DIMENSION = get_settings().embedding_dimension


@pytest.fixture()
async def db_engine():
    """Fresh engine per test — lives in the same event loop as the test."""
    engine = create_async_engine(DATABASE_URL)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
    await engine.dispose()


@pytest.fixture()
async def session(db_engine):
    factory = async_sessionmaker(db_engine, expire_on_commit=False)
    async with factory() as s:
        yield s


async def test_vector_extension_enabled(db_engine):
    async with db_engine.connect() as conn:
        result = await conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        )
        assert result.scalar() == "vector"


async def test_all_tables_created(db_engine):
    async with db_engine.connect() as conn:
        tables = await conn.run_sync(lambda c: inspect(c).get_table_names())
    assert set(tables) >= {"airports", "flights", "notams", "sops"}


async def test_airport_insert_and_query(db_engine, session):
    airport = Airport(icao_code="KJFK", iata_code="JFK", name="John F. Kennedy International")
    session.add(airport)
    await session.commit()
    await session.refresh(airport)

    result = await session.get(Airport, airport.id)
    assert result is not None
    assert result.icao_code == "KJFK"


async def test_flight_insert_and_query(db_engine, session):
    flight = Flight(flight_number="AA100", status="scheduled")
    session.add(flight)
    await session.commit()
    await session.refresh(flight)

    result = await session.get(Flight, flight.id)
    assert result is not None
    assert result.flight_number == "AA100"


async def test_notam_with_embedding(db_engine, session):
    notam = Notam(
        notam_id="KJFK/NOTAM001",
        raw_text="Runway 13R/31L closed for maintenance.",
        embedding=[0.1] * EMBEDDING_DIMENSION,
    )
    session.add(notam)
    await session.commit()
    await session.refresh(notam)

    result = await session.get(Notam, notam.id)
    assert result is not None
    assert result.notam_id == "KJFK/NOTAM001"
    assert len(result.embedding) == EMBEDDING_DIMENSION


async def test_sop_with_embedding(db_engine, session):
    sop = Sop(
        title="Departure Briefing SOP",
        content="Verify weather minima before departure.",
        category="departure",
        embedding=[0.2] * EMBEDDING_DIMENSION,
    )
    session.add(sop)
    await session.commit()
    await session.refresh(sop)

    result = await session.get(Sop, sop.id)
    assert result is not None
    assert result.title == "Departure Briefing SOP"
    assert len(result.embedding) == EMBEDDING_DIMENSION
