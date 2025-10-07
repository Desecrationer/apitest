import os
import psycopg
from fastapi import FastAPI, Request
from psycopg.rows import dict_row

app = FastAPI()

# # Railway will provide DATABASE_URL automatically if you add a Postgres db to your project.
# e.g. postgres://USER:PASSWORD@HOST:PORT/DBNAME
DATABASE_URL = os.environ.get("DATABASE_URL")

# # Create table on startup (id auto-increments)
# @app.on_event("startup")
# def init_db():
#     with psycopg.connect(DATABASE_URL, autocommit=True) as conn:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 CREATE TABLE IF NOT EXISTS players (
#                     id SERIAL PRIMARY KEY,
#                     username TEXT UNIQUE NOT NULL,
#                     health INTEGER NOT NULL
#                 )
#             """)

@app.post("/player/create_player")
async def create_player(request: Request):
    data = await request.json()
    character_name= data.get("character_name")
    isStateless = data.get("isStateless")
    created_at = data.get("created_at")
    last_login = data.get("last_login")

    if not character_name or isStateless is None:
        return {"error": "character_name and stateless state are required"}

    # Insert or update by username
    sql = """
      INSERT INTO player (character_name, isStateless, created_at, last_login)
      VALUES (%s, %s, %s, %s)
      ON CONFLICT (character_name) DO UPDATE SET isStateless = EXCLUDED.isStateless
      RETURNING player_id, character_name, isStateless, created_at, last_login
    """
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (character_name, isStateless, created_at, last_login))
            row = cur.fetchone()
    return {"message": "Player upserted", "player": row}
6
@app.get("/player/{player_id}")
def get_player(player_id: int):
    sql = "SELECT player_id, character_name, isStateless, created_at, last_login FROM player WHERE player_id = %s"
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (player_id,))
            row = cur.fetchone()
            if not row:
                return {"error": "Player not found"}
            return row


@app.get("/player/{player_id}/state")
def get_player(player_id: int):
    sql = "SELECT isStateless FROM player WHERE player_id = %s"
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (player_id,))
            row = cur.fetchone()
            if not row:
                return {"error": "Player not found"}
            return row