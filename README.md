# stocktake

> **Practice exercise.** This repo is intentionally broken and insecure. It exists for
> DevSecOps interview practice. Do not deploy it anywhere.

A small inventory service: a Flask API behind nginx, with Postgres for storage and Redis
for caching.

```
client ──▶ proxy (nginx :8080) ──▶ app (Flask/gunicorn) ──▶ db (Postgres)
                                                      └───▶ cache (Redis)
```

## Your task (about 60 minutes)

Get the stack running end to end, then clean up anything you wouldn't ship.

```bash
docker compose up --build
```

You're done when all of these work through the proxy:

```bash
curl -s localhost:8080/health          # {"status": "ok"}
curl -s localhost:8080/items           # the seeded inventory
curl -s localhost:8080/items/search?q=tomato
curl -s -X POST localhost:8080/items -H 'content-type: application/json' \
     -d '{"name": "basil", "quantity": 12}'
curl -s localhost:8080/stats           # total quantity, cached for 30s
```

Talk through what you're doing as you go. How you debug matters more than how fast.
Docs, Google and man pages are all fair game.

There is also a CI pipeline the team wants to enable in `ci/ci.yml`. Have a look at it
when the stack is up.
