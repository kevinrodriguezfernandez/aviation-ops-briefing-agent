"""Minimal smoke tests for src/db models and connection."""

import pytest
from sqlalchemy import inspect, text

from src.db.connection import AsyncSessionFactory, engine, init_db
from src.db.models import Airport, Flight, Notam, Sop


@pytest.fixture(autouse=True)
async def setup_db():
    await init_db()
    yield
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))


async def test_vector_extension_enabled():
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        )
        assert result.scalar() == "vector"


async def test_all_tables_created():
    async with engine.connect() as conn:
        tables = await conn.run_sync(lambda c: inspect(c).get_table_names())
    assert set(tables) >= {"airports", "flights", "notams", "sops"}


async def test_airport_insert_and_query():
    async with AsyncSessionFactory() as session:
        airport = Airport(icao_code="KJFK", iata_code="JFK", name="John F. Kennedy International")
        session.add(airport)
        await session.commit()
        await session.refresh(airport)

    async with AsyncSessionFactory() as session:
        result = await session.get(Airport, airport.id)
        assert result is not None
        assert result.icao_code == "KJFK"


async def test_flight_insert_and_query():
    async with AsyncSessionFactory() as session:
        flight = Flight(flight_number="AA100", status="scheduled")
        session.add(flight)
        await session.commit()
        await session.refresh(flight)

    async with AsyncSessionFactory() as session:
        result = await session.get(Flight, flight.id)
        assert result is not None
        assert result.flight_number == "AA100"


async def test_notam_with_embedding():
    async with AsyncSessionFactory() as session:
        notam = Notam(
            notam_id="KJFK/NOTAM001",
            raw_text="Runway 13R/31L closed for maintenance.",
            embedding=[0.1] * 1536,
        )
        session.add(notam)
        await session.commit()
        await session.refresh(notam)

    async with AsyncSessionFactory() as session:
        result = await session.get(Notam, notam.id)
        assert result is not None
        assert result.notam_id == "KJFK/NOTAM001"
        assert len(result.embedding) == 1536


async def test_sop_with_embedding():
    async with AsyncSessionFactory() as session:
        sop = Sop(
            title="Departure Briefing SOP",
            content="Verify weather minima before departure.",
            category="departure",
            embedding=[0.2] * 1536,
        )
        session.add(sop)
        await session.commit()
        await session.refresh(sop)

    async with AsyncSessionFactory() as session:
        result = await session.get(Sop, sop.id)
        assert result is not None
        assert result.title == "Departure Briefing SOP"
        assert len(result.embedding) == 1536
