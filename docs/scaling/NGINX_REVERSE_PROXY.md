# Native Nginx Reverse Proxy

Nginx is prepared as an optional local entry point without Docker. It listens
on port 8080, sends API and operational routes to FastAPI on port 8000, and
sends all other routes to Next.js on port 3000.

```text
Browser / client -> Nginx :8080 -> FastAPI :8000
                              \-> Next.js :3000
```

## Install

On macOS with Homebrew:

```bash
brew install nginx
```

The repository uses the Homebrew executable directly, so it does not require a
system-wide configuration change or a background Homebrew service.

## Run

Start each process in a separate terminal:

```bash
make nginx-api
make nginx-web
make nginx-start
```

Open `http://localhost:8080`. The frontend command configures its browser API
URL as `http://localhost:8080/api/v1`, keeping browser traffic on one origin.

Useful lifecycle commands:

```bash
make nginx-test
make nginx-status
make nginx-reload
make nginx-stop
```

Runtime PID, access logs, error logs, and temporary files are written beneath
the ignored `.nginx-runtime/` directory. The checked-in configuration remains
under `ops/nginx/`.

## Routes

| Public route | Upstream |
| --- | --- |
| `/api/*` | FastAPI |
| `/health`, `/health/ready`, `/metrics` | FastAPI |
| `/docs*`, `/redoc*`, `/openapi.json` | FastAPI |
| `/nginx-health` | Nginx local health response |
| Everything else | Next.js |

Nginx forwards the host, client address, scheme, and a correlation ID. If the
client supplies `X-Request-ID`, that value is preserved; otherwise Nginx creates
one and FastAPI includes it in its structured request log and response.

## Scaling-lab status

This setup is prepared infrastructure only. It does not change the Phase 1
baseline architecture or its results. Load tests continue to target
`http://127.0.0.1:8000` until a later experiment explicitly tests Nginx or uses
it to distribute traffic across multiple stateless application instances.

TLS is intentionally not configured for localhost. A deployed environment must
use managed certificates, redirect HTTP to HTTPS, restrict access to `/metrics`,
and define trusted proxy boundaries before relying on forwarded client headers.
