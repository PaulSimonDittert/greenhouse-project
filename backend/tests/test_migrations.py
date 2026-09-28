import os

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not TEST_DATABASE_URL, reason="Set TEST_DATABASE_URL to an isolated PostgreSQL test database")


def test_migrations_upgrade_empty_database_to_head():
    from infrastructure.settings import settings

    engine = create_engine(TEST_DATABASE_URL)
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP SCHEMA public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))

        alembic_config = Config("alembic.ini")
        development_database_url = settings.database_url
        settings.database_url = TEST_DATABASE_URL
        try:
            command.upgrade(alembic_config, "head")
        finally:
            settings.database_url = development_database_url

        with engine.connect() as connection:
            tables = set(connection.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            )).scalars())
            revision = connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()

        assert {"devices", "locations", "zones", "alembic_version"}.issubset(tables)
        assert revision == "779ded18505f"
    finally:
        engine.dispose()