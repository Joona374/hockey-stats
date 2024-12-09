from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.models import Player as PlayerRow

from api.models import PlayerResponse
from api.db_communicators import getAllPlayers, getOnePlayer

app = FastAPI()

# Dependecy that creates a Session for each request.
def getSession():
    dbSession = SessionLocal()  # Create a new one time use session
    try:
        yield dbSession         # Return the session to be used in endpoint
    finally:    
        dbSession.close()       # Ensure session is closed after use



@app.get("/players/", response_model=dict[str, PlayerResponse])
def list_players():
    players = getAllPlayers()
    return players

@app.get("/players/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(getSession)):
    Player = getOnePlayer(player_id)
    return Player