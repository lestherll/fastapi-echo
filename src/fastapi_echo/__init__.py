from typing import Any

from fastapi import FastAPI, Request

app = FastAPI(title="fastapi-echo")


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
        return {"echo": await request.json()}
    except ValueError:
        return {"echo": body.decode(errors="replace")}
