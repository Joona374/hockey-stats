from pydantic import BaseModel
from typing import Optional, List

class playerSeasonLevelResponse(BaseModel):
    """
    Represents a response model for a player's performance in one level
    (e.g. "U16 AAA" or "U18 Mestis") in a season. This model is not directly
    equivalent to a database model, but is instead created in
    api.db_communicators.py by combining data from the "player_seasons" and
    "player_season_level" tables.

    The "clubName", "levelName" and "ageGroupName" fields are not present in
    the database model, but are added here to make the API more convenient to
    use.
    """
    id: int
    clubId: int
    clubName: Optional[str]
    levelId: int
    levelName: Optional[str]
    ageGroupId: int
    ageGroupName: Optional[str]
    seasonId: int
    playerId: int

    games: int
    goals: int
    assists: int
    points: int
    penaltyMinutes: int

    class Config:
        from_attributes = True

class playerSeasonResponse(BaseModel):
    """
    Represents a response model for a season in the API. This does not directly
    correspond to a database model, but is instead created in
    api.db_communicators.py by combining data from the "player_seasons" and
    "player_season_level" tables. The "seasonLevels" field is a list of
    playerSeasonLevelResponse objects, which are not present in the database
    model.
    """
    id: int
    year: int
    games: int
    goals: int
    assists: int
    points: int
    penaltyMinutes: int
    ppGoals: int
    shGoals: int
    soGoals: int
    playerId: int

    # List of seasonLevels that are part of this season. This is not present in the database model, but its created in api.db_communicators.py
    seasonLevels: Optional[List[playerSeasonLevelResponse]] = None 

    class Config:
        from_attributes = True

class PlayerResponse(BaseModel):
    """
    Represents a response model for a player in the API. This does not directly
    correspond to a database model, but is instead created in
    api.db_communicators.py by combining data from the "players" table and
    optionally the "playerSeasons" table. The "seasons" field is a list of
    playerSeasonResponse objects, which are not present in the database model,
    but its created in api.db_communicators.py
    """

    id: int
    sjlName: str
    epName: str
    sjlLink: str
    birthYear: int
    position: str
    
    # List of seasons the player has played. This is not present in the database model, but its created in api.db_communicators.py
    seasons: Optional[List[playerSeasonResponse]] = None  

    class Config:
        from_attributes = True

