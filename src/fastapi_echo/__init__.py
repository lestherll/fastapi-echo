import os
from contextlib import asynccontextmanager
from typing import Any

import asyncpg
from fastapi import FastAPI, Request

# DATABASE_URL_MAIN, not DATABASE_URL: the platform injects one variable per
# attached database, suffixed with that attachment's alias (`as: main` in
# deploy/application.yaml). The suffix is unconditional — there is no bare
# name for the single-database case — so that adding a second database later
# is purely additive instead of silently changing what DATABASE_URL means.
DATABASE_URL = os.environ["DATABASE_URL_MAIN"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
    async with app.state.pool.acquire() as conn:
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS echoes (
                id serial PRIMARY KEY,
                message text NOT NULL,
                created_at timestamptz NOT NULL DEFAULT now()
            )
            """
        )
    yield
    await app.state.pool.close()


app = FastAPI(title="fastapi-echo", lifespan=lifespan)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "fastapi-echo is running"}


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/echo/{message}")
def echo_path(message: str) -> dict[str, str]:
    return {"echo": message}


@app.post("/echo")
async def echo_body(request: Request) -> dict[str, Any]:
    body = await request.body()
    if not body:
        return {"echo": None}
    try:
        parsed = await request.json()
    except ValueError:
        parsed = body.decode(errors="replace")

    async with request.app.state.pool.acquire() as conn:
        await conn.execute("INSERT INTO echoes (message) VALUES ($1)", str(parsed))
    return {"echo": parsed}


@app.get("/echo-history")
async def echo_history(request: Request) -> list[dict[str, Any]]:
    async with request.app.state.pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, message, created_at FROM echoes ORDER BY id DESC LIMIT 20"
        )
    return [dict(row) for row in rows]
