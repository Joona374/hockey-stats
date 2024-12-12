from fastapi import FastAPI, Query, Request, HTTPException
from typing import Optional, Union
from sqlalchemy.orm import Session

from database.connection import SessionLocal
from database.models import Player as PlayerRow

from api.models import PlayerResponse, GoalieResponse, seasonLevelResponse
from api.db_communicators import getAllPlayers, getOnePlayer, getFilteredSeasonLevels

# Init the FastAPI app
app = FastAPI()

# Dependecy that creates a Session for each request.
# Currently this is not used anywhere, but lets keep it here just in case.
def getSession():
    dbSession = SessionLocal()  # Create a new one time use session
    try:
        yield dbSession         # Return the session to be used in endpoint
    finally:    
        dbSession.close()       # Ensure session is closed after use



@app.get("/players/", response_model=dict[str, PlayerResponse])
def list_players():
    """
    Returns all players in the database.

    Returns a dictionary with the following structure:
    {
        "Player1 sjlName": Player1 (PlayerResponse),
        "Player2 sjlName": Player2 (PlayerResponse),
        ...
    }
    Each PlayerResponse object has the attributes documented in api/models.py
    """
    players = getAllPlayers()
    return players

@app.get("/players/{player_id}", response_model=Union[GoalieResponse, PlayerResponse])
def get_player(player_id: int):
    """
    Returns one player by id.

    Args:
        player_id (int): The id of the player to read.

    Returns:
        Union[GoalieResponse, PlayerResponse]: The player object read from the database.
        Each player object has custom made "seasons" attribute, which is a list containing the seasons for the player.
        Each season object has custom made "seasonLevels" attribute, which is a list containing the seasonLevel objects for the season.
    """
    Player = getOnePlayer(player_id)
    return Player

@app.get("/season-levels", response_model=seasonLevelResponse)
def getFilteredSeasons(
    request: Request,
    position: Optional[str] = Query(None),
    clubName: Optional[str] = Query(None),
    levelName: Optional[str] = Query(None),
    ageGroupName: Optional[str] = Query(None),
    sjlName: Optional[str] = Query(None),
    year: Optional[str] = Query(None),
    clubID: Optional[int] = Query(None),
    levelId: Optional[int] = Query(None),
    ageGroupId: Optional[int] = Query(None),
    seasonId: Optional[int] = Query(None),
    playerId: Optional[int] = Query(None),
    ):

    """
    Endpoint to retrieve season levels filtered by various criteria.

    This endpoint allows clients to query for season levels by providing
    optional query parameters. The response is a list of season levels 
    that match the specified filters.

    Query Parameters:
        request (Request): The HTTP request object.
        position (Optional[str]): The position of the player (e.g., "Maalivahti").
        clubName (Optional[str]): The name of the club.
        levelName (Optional[str]): The name of the level.
        ageGroupName (Optional[str]): The name of the age group.
        sjlName (Optional[str]): The SJL name of the player.
        year (Optional[str]): The year of the season.
        clubID (Optional[int]): The ID of the club.
        levelId (Optional[int]): The ID of the level.
        ageGroupId (Optional[int]): The ID of the age group.
        seasonId (Optional[int]): The ID of the season.
        playerId (Optional[int]): The ID of the player.

    Returns:
        seasonLevelResponse: A response model containing lists of goalie and player season levels.

    Raises:
        HTTPException: If any invalid query parameters are provided.
    """

    # If there are invalid keys in the query we inform the user before even trying to get the data
    AcceptedKeys = {"position", "clubName", "levelName", "ageGroupName", "sjlName", "year", "clubId", "levelId", "ageGroupId", "seasonId", "playerId"} # Set of accepted query keys
    QueryKeys = set(request.query_params.keys())    # Gets a set of all the query keys used in a request
    InvalidKeys = QueryKeys - AcceptedKeys          # Finds the invalid keys by subtracting the accepted keys from the query keys, if any remain, these are invalid
    if len(InvalidKeys) > 0:                        # If there are any invalid keys we raise the exception informing the user about incorrect keys used
        Message = f"Invalid query parameters: {', '.join(InvalidKeys)}"
        raise HTTPException(status_code=400, detail=Message)

    # If there are no invalid keys we get the filtered season level objects and return them inside the seasonLevelResponse model defined in api/models.py
    Filters = {"position": position, "levelName": levelName, "clubName": clubName, "ageGroupName": ageGroupName, "sjlName": sjlName, "year": year, "clubId": clubID, "levelId": levelId, "ageGroupId": ageGroupId, "seasonId": seasonId, "playerId": playerId}
    return getFilteredSeasonLevels(Filters)
