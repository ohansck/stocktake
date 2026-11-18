import logging
import os
import traceback

import psycopg2
import redis
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("stocktake")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "stocktake-dev-secret")

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("POSTGRES_DB", "stocktake")
DB_USER = os.environ.get("POSTGRES_USER", "stocktake")
DB_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

log.info("using database postgres://%s:%s@%s/%s", DB_USER, DB_PASSWORD, DB_HOST, DB_NAME)

cache = redis.Redis.from_url(REDIS_URL)


def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=3,
    )


def to_items(rows):
    return [{"id": r[0], "name": r[1], "quantity": r[2]} for r in rows]


@app.get("/health")
def health():
    try:
        with get_db() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
        cache.ping()
        return jsonify(status="ok")
    except Exception as e:
        return jsonify(status="error", detail=str(e)), 500


@app.get("/items")
def list_items():
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, name, quantity FROM items ORDER BY id")
        rows = cur.fetchall()
    return jsonify(to_items(rows))


@app.get("/items/search")
def search_items():
    q = request.args.get("q", "")
    with get_db() as conn, conn.cursor() as cur:
        cur.execute(f"SELECT id, name, quantity FROM items WHERE name ILIKE '%{q}%' ORDER BY id")
        rows = cur.fetchall()
    return jsonify(to_items(rows))


@app.post("/items")
def create_item():
    data = request.get_json()
    with get_db() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO items (name, quantity) VALUES (%s, %s) RETURNING id",
            (data["name"], data["quantity"]),
        )
        new_id = cur.fetchone()[0]
    cache.delete("stats")
    return jsonify(id=new_id), 201


@app.get("/stats")
def stats():
    cached = cache.get("stats")
    if cached is not None:
        return jsonify(total_quantity=int(cached), cached=True)
    with get_db() as conn, conn.cursor() as cur:
        cur.execute("SELECT COALESCE(SUM(quantity), 0) FROM items")
        total = cur.fetchone()[0]
    cache.set("stats", total, ex=30)
    return jsonify(total_quantity=total, cached=False)


# Handy while we were wiring up the environment variables.
@app.get("/debug/env")
def debug_env():
    return jsonify(dict(os.environ))


@app.errorhandler(Exception)
def handle_error(e):
    return jsonify(error=str(e), trace=traceback.format_exc()), 500
