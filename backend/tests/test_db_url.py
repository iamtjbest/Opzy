import pytest

from app.core.db import build_engine_args


def test_translates_sslmode_to_asyncpg_ssl():
    url, connect_args, _ = build_engine_args(
        "postgresql://u:p@db.example.supabase.co:5432/postgres?sslmode=require"
    )
    assert url.startswith("postgresql+asyncpg://")
    assert "sslmode" not in url
    assert connect_args["ssl"] is True


def test_pooler_port_disables_statement_caches():
    # pgbouncer in transaction mode makes asyncpg's cached statements collide. Both
    # caches have to travel in connect_args: that's the only place SQLAlchemy's asyncpg
    # dialect and asyncpg itself will actually pick `prepared_statement_cache_size` and
    # `statement_cache_size` up from — passing either as a bare create_engine keyword
    # raises TypeError, since create_engine itself has no such argument.
    _, connect_args, engine_kwargs = build_engine_args(
        "postgresql://u:p@db.example.supabase.co:6543/postgres"
    )
    assert connect_args["statement_cache_size"] == 0
    assert connect_args["prepared_statement_cache_size"] == 0
    assert engine_kwargs == {}


def test_direct_port_keeps_statement_caches():
    _, connect_args, engine_kwargs = build_engine_args(
        "postgresql://u:p@db.example.supabase.co:5432/postgres"
    )
    assert "statement_cache_size" not in connect_args
    assert "prepared_statement_cache_size" not in connect_args
    assert engine_kwargs == {}


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://postgres:[YOUR-PASSWORD]@db.example.supabase.co:5432/postgres",
        "postgresql://postgres:pa]ss@db.example.supabase.co:5432/postgres",
    ],
)
def test_unencoded_password_gives_a_readable_error(url):
    with pytest.raises(RuntimeError, match="percent-encode"):
        build_engine_args(url)
