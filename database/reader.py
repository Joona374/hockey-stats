from database.connection import SessionLocal
from database.models import Player, PlayerSeason, GoalieSeason, PlayerSeasonLevel, GoalieSeasonLevel, Club, Level, AgeGroup

def readOneClub(Session: object, clubId: int) -> object:
    """
    Queries the database and returns the Club row object with the given id.
    """
    return Session.query(Club).filter_by(id=clubId).first()

def readOneLevel(Session: object, levelId: int) -> object:
    """
    Queries the database and returns the Level row object with the given id.
    """
    return Session.query(Level).filter_by(id=levelId).first()

def readOneAgeGroup(Session: object, ageGroupId: int) -> object:
    """
    Queries the database and returns the AgeGroup row object with the given id.
    """
    return Session.query(AgeGroup).filter_by(id=ageGroupId).first()

def readOnePlayer(Session: object, playerId: int) -> object:
    """
    Queries the database and returns the Player object with the given id.
    """
    return Session.query(Player).filter_by(id=playerId).first()

def readPlayersSeasons(Session: object, playerId: int, Position: str = None) -> list:
    """
    Queries the database and returns all Seasons for the player with the given id.
    Args: 
        Session (object): The SQLAlchemy session to use for the query.
        playerId (int): The id of the player to read.
        Position (str): The position of the player, either "Maalivahti", "Hyökkääjä", "Puolustaja" or "Kenttäpelaaja".
    """
    if Position is None:                                                  # In case a Position is not provided in call (as should)
        PlayerRow = Session.query(Player).filter_by(id=playerId).first()  # Query the database to find the player row
        if PlayerRow is None:                                             # If its not found then something is wrong
            raise Exception("Player not found!")                          # Raise an exception

    Position = PlayerRow.position                                         # Get the player's position from the actual player row

    if Position == "Maalivahti":                                          # If the player is a goalie, return all GoalieSeason objects that match the player id
        return Session.query(GoalieSeason).filter_by(playerId=playerId).all()
    else:                                                                 # Else return all PlayerSeason objects that match the player id
        return Session.query(PlayerSeason).filter_by(playerId=playerId).all()

def readLevelsForSeason(Session: object, PseasonId: int, Position: str = None) -> list:
    """
    Queries the database and returns all SeasonLevels for the given playerSeasonId.
    It also writes custom .clubName, .leveName and .ageGroupName attributes to the SeasonLevel objects.
    These are needed for the pydantic model.
    
    Args:
        Session (object): The SQLAlchemy session to use for the query.
        PseasonId (int): The id of the playerSeason row in the playerSeasons table.
        Position (str): The position of the player. Defaults to None. 

    Returns:
        list: A list of SeasonLevel objects. If the player is a goalie, the list contains GoalieSeasonLevel objects, otherwise PlayerSeasonLevel objects. Custom clubName, levelName and ageGroupName attributes for pydantic model.
    """
    ### THIS IS GOING TO CRASH IF POSITION IS NONE ###
    ### NEEDS TO BE FIXED! ###
    if Position is None:
        raise Exception("Position is None!")

    if Position == "Maalivahti": 
        SeasonLevels = Session.query(GoalieSeasonLevel).filter_by(seasonId=PseasonId).all()     # Finds all the goalieSeasonLevel rows that match the Season rows id
    else:
        SeasonLevels = Session.query(PlayerSeasonLevel).filter_by(seasonId=PseasonId).all()     # Finds all the playerSeasonLevel rows that match the Season rows id

    for SeasonLevel in SeasonLevels:
        # Write the custom names to each SeasonLevel object. This is needed for the pydantic model
        # The functions used are from the same module, and return the whole row.
        # Thats why we use ".clubName" for example, to just acces the desired name, not the object itself.
        SeasonLevel.clubName = readOneClub(Session, SeasonLevel.clubId).clubName 
        SeasonLevel.levelName = readOneLevel(Session, SeasonLevel.levelId).levelName
        SeasonLevel.ageGroupName = readOneAgeGroup(Session, SeasonLevel.ageGroupId).ageGroupName
    
    return SeasonLevels # Return the list of seasonsLevel rows with new custom attributes.

def readAllPlayers(Session: object) -> list:
    """
    Queries the database and returns all contents of the "players" table. Return just the basic info, no seasons.
    """
    return Session.query(Player).all()

def parsePlayersToDict(Players: list) -> dict:
    """
    Parses the list of Player objects into a dictionary with the sjlName as the key and the Player object as the value. No seasons.
    """
    PlayersDict = {}
    for Player in Players:
        PlayersDict[Player.sjlName] = Player
    return PlayersDict

def getAllClubs(Session: object) -> list:
    """
    Queries the database and returns all contents of the "clubs" table.
    """
    return Session.query(Club).all()

def parseClubsToDict(Clubs: list) -> dict:
    """
    Parses the list of Club objects into a dictionary with the clubName as the key and the Club object as the value.
    """
    ClubsDict = {}
    for Club in Clubs:
        ClubsDict[Club.clubName] = Club
    return ClubsDict

def getAllLevels(Session: object) -> list:
    """
    Queries the database and returns all contents of the "levels" table.
    """
    return Session.query(Level).all()

def parseLevelsToDict(Levels: list) -> dict:
    """
    Parses the list of Level objects into a dictionary with the levelName as the key and the Level object as the value.
    """
    LevelsDict = {}
    for Level in Levels:
        LevelsDict[Level.levelName] = Level
    return LevelsDict

def getAllAgeGroups(Session: object) -> list:
    """
    Queries the database and returns all contents of the "age_groups" table.
    """
    return Session.query(AgeGroup).all()

def parseAgeGroupsToDict(AgeGroups: list) -> dict:
    """
    Parses the list of AgeGroup objects into a dictionary with the ageGroupName as the key and the AgeGroup object as the value.
    """
    AgeGroupsDict = {}
    for AgeGroup in AgeGroups:
        AgeGroupsDict[AgeGroup.ageGroupName] = AgeGroup
    return AgeGroupsDict

def getDbContents():

    """
    Queries the database and returns all contents of the "players", "clubs", "levels" and "age_groups" tables
    in a single dictionary.
    
    Returns a dictionary with the following structure:
    {
        "Players": {
            "Player1 sjlName": Player1,
            "Player2 sjlName": Player2,
            ...
        },
        "Clubs": {
            "Club1 name": Club1,
            "Club2 name": Club2,
            ...
        },
        "Levels": {
            "Level1 name": Level1,
            "Level2 name": Level2,
            ...
        },
        "AgeGroups": {
            "AgeGroup1 name": AgeGroup1,
            "AgeGroup2 name": AgeGroup2,
            ...
        }
    }
    """
    Session = SessionLocal()

    PlayersList = readAllPlayers(Session)
    PlayersDict = parsePlayersToDict(PlayersList)

    ClubsList = getAllClubs(Session)
    ClubsDict = parseClubsToDict(ClubsList)
    
    LevelsList = getAllLevels(Session)
    LevelsDict = parseLevelsToDict(LevelsList)
    
    AgeGroupsList = getAllAgeGroups(Session)
    AgeGroupsDict = parseAgeGroupsToDict(AgeGroupsList)
    
    Session.close()

    return {"players": PlayersDict, "clubs": ClubsDict, "levels": LevelsDict, "ageGroups": AgeGroupsDict}

