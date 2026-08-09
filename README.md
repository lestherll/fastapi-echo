# fastapi-echo

Minimal FastAPI echo server — a test instance for the homelab's GitOps deploy
pattern (no database, no state).

## Endpoints

- `GET /` — sanity check
- `GET /healthz` — k8s probe target
- `GET /echo/{message}` — echoes the path segment
- `POST /echo` — echoes the request body (JSON, text, or empty)

## Local dev

```
uv sync
uv run uvicorn fastapi_echo:app --reload
```

## Container

```
podman build -t fastapi-echo:local .
podman run -p 8000:8000 fastapi-echo:local
```

## Deploy

`deploy/` holds the Kubernetes manifests (Kustomize). Applied via Flux from
the `homelab` repo — see `infrastructure/fastapi-echo/` there for the
`GitRepository`/`Kustomization` wiring.
