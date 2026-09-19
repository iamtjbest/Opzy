from collections.abc import AsyncGenerator
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

SUPABASE_POOLER_PORT = 6543


def build_engine_args(url: str) -> tuple[str, dict, dict]:
    try:
        parsed = urlsplit(url)
    except ValueError as exc:
        # A password containing URL-reserved characters (brackets, @, /, #, ?) breaks
        # parsing before anything connects. Supabase's copied string also arrives with a
        # literal [YOUR-PASSWORD] placeholder, which fails the same way.
        raise RuntimeError(
            "DATABASE_URL could not be parsed. If the password contains special "
            "characters, percent-encode them ([ is %5B, ] is %5D, @ is %40), and make "
            "sure any [YOUR-PASSWORD] placeholder has been replaced."
        ) from exc
    query = dict(parse_qsl(parsed.query))
    connect_args: dict = {}
    engine_kwargs: dict = {}

    # asyncpg has no `sslmode` param (that is a libpq/psycopg spelling), but Supabase
    # requires TLS, so translate it into asyncpg's `ssl` instead of passing it through.
    if query.pop("sslmode", None) is not None:
        connect_args["ssl"] = True

    try:
        port = parsed.port
    except ValueError:
        port = None

    # Supabase's pooled endpoint runs pgbouncer in transaction mode, where prepared
    # statements leak across pooled sessions and collide. Both caches must be off.
    if port == SUPABASE_POOLER_PORT:
        connect_args["statement_cache_size"] = 0
        engine_kwargs["prepared_statement_cache_size"] = 0

    async_url = urlunsplit(
        ("postgresql+asyncpg", parsed.netloc, parsed.path, urlencode(query), parsed.fragment)
    )
    return async_url, connect_args, engine_kwargs


_settings = get_settings()
_url, _connect_args, _engine_kwargs = build_engine_args(_settings.database_url)

engine = create_async_engine(
    _url,
    pool_pre_ping=True,
    echo=_settings.sql_echo,
    connect_args=_connect_args,
    **_engine_kwargs,
)

SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
