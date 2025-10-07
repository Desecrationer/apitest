import os
import psycopg
from fastapi import FastAPI, Request
from psycopg.rows import dict_row

app = FastAPI()

# Railway will provide DATABASE_URL automatically if you add a Postgres db to your project.
# e.g. postgres://USER:PASSWORD@HOST:PORT/DBNAME
DATABASE_URL = os.environ.get("DATABASE_URL")

@app.post("/player/create_player")
async def create_player(request: Request):
    """
    Creates a new player in the database. Should be called when intializing the game.
    """
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


@app.post("/player/{player_id}/update_last_login")
async def update_last_login(player_id:int, request: Request):
    """
    Updates the timestamp of when the player last logged in. Should be updated each time a player logs in.
    """
    data = await request.json()
    last_login = data.get("last_login")
    sql = """
      UPDATE player
      SET last_login = {last_login} WHERE player_id = {player_id}
      RETURNING player_id, character_name, isStateless, created_at, last_login
    """
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (last_login, player_id))
            row = cur.fetchone()
    return {"message": "Login Updated", "player": row}



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
def get_player_state(player_id: int):
    sql = "SELECT isStateless FROM player WHERE player_id = %s"
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (player_id,))
            row = cur.fetchone()
            if not row:
                return {"error": "Player not found"}
            return row