from fastapi import FastAPI, Request

app = FastAPI()

# pretend database
players = {}

@app.post("/player")
async def create_player(request: Request):
    # parse raw JSON body
    data = await request.json()
    username = data.get("username")
    health = data.get("health")

    if not username or health is None:
        return {"error": "username and health are required"}

    # save to in-memory dict
    players[username] = {"username": username, "health": health}
    return {"message": f"Player '{username}' created", "player": players[username]}

@app.get("/player/{username}")
def get_player(username: str):
    if username not in players:
        return {"error": "Player not found"}
    return players[username]
