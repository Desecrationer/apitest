import os
import psycopg
from fastapi import FastAPI, Request
from psycopg.rows import dict_row

app = FastAPI()

# Railway will provide DATABASE_URL automatically if you add a Postgres db to your project.
# e.g. postgres://USER:PASSWORD@HOST:PORT/DBNAME
DATABASE_URL = os.environ.get("DATABASE_URL")

# Create table on startup (id auto-increments)
@app.on_event("startup")
def init_db():
    with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    health INTEGER NOT NULL
                )
            """)

@app.post("/player")
async def create_player(request: Request):
    data = await request.json()
    username = data.get("username")
    health = data.get("health")

    if not username or health is None:
        return {"error": "username and health are required"}

    # Insert or update by username
    sql = """
      INSERT INTO players (username, health)
      VALUES (%s, %s)
      ON CONFLICT (username) DO UPDATE SET health = EXCLUDED.health
      RETURNING id, username, health
    """
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (username, health))
            row = cur.fetchone()
    return {"message": "Player upserted", "player": row}

@app.get("/player/{username}")
def get_player(username: str):
    sql = "SELECT id, username, health FROM players WHERE username = %s"
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (username,))
            row = cur.fetchone()
            if not row:
                return {"error": "Player not found"}
            return row
