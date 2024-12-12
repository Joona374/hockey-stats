from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.models import Player, PlayerSeason, GoalieSeason, PlayerSeasonLevel, GoalieSeasonLevel, Club, Level, AgeGroup


def readOneClubById(PSession: Session, clubId: int) -> object:
    """
    Queries the database and returns the Club row object with the given id.
    """
    return PSession.query(Club).filter_by(id=clubId).first()

def readOneClubByName(PSession: Session, PClubName: str) -> object:
    """
    Queries the database and returns the Club row object with the given name.
    """
    return PSession.query(Club).filter_by(clubName=PClubName).first()

def readOneLevelById(PSession: Session, levelId: int) -> object:
    """
    Queries the database and returns the Level row object with the given id.
    """
    return PSession.query(Level).filter_by(id=levelId).first()

def readOneLevelByName(PSession: Session, PLevelName: str) -> object:
    """ 
    Queries the database and returns the Level row object with the given name.
    """
    return PSession.query(Level).filter_by(levelName=PLevelName).first()

def readOneAgeGroupById(PSession: Session, ageGroupId: int) -> object:
    """
    Queries the database and returns the AgeGroup row object with the given id.
    """
    return PSession.query(AgeGroup).filter_by(id=ageGroupId).first()

def readOneAgeGroupByName(PSession: Session, PAgeGroupName: str) -> object:
    """
    Queries the database and returns the AgeGroup row object with the given name.
    """
    return PSession.query(AgeGroup).filter_by(ageGroupName=PAgeGroupName).first()

def readOnePlayerById(PSession: Session, playerId: int) -> object:
    """
    Queries the database and returns the Player object with the given id.
    """
    return PSession.query(Player).filter_by(id=playerId).first()

def readOnePlayerByName(PSession: Session, PPlayerName: str) -> object:
    """
    Queries the database and returns the Player object with the given name.
    """
    return PSession.query(Player).filter_by(sjlName=PPlayerName).first()

def convertNamesToIds(Filters: dict, PSession: Session) -> None:
    """
    Converts the given name filter parameters to id filter parameters.
    Ex. "clubName": "Pelicans" gets deleted, and "clubId": 3 is added.
    This is done because seasonLevel tables dont store the string names, but ids. 
    Edits the Filters dict in place without returning anything.
    
    Args:
        Filters (dict): The dictionary containing the name filters. Is edited in place
        PSession (Session): The database session object to connect to the db.
    
    Returns:
        None
    """
    if "clubName" in Filters:                                                               # If clubName is given as filter
        Filters["clubId"] = readOneClubByName(PSession, Filters["clubName"]).id             # Get the id of the club
        del Filters["clubName"]                                                             # Delete the name from the filters dict

    if "levelName" in Filters:                                                              # If levelName is given as filter
        Filters["levelId"] = readOneLevelByName(PSession, Filters["levelName"]).id          # Get the id of the level
        del Filters["levelName"]                                                            # Delete the name from the filters dict

    if "ageGroupName" in Filters:                                                           # If ageGroupName is given as filter
        Filters["ageGroupId"] = readOneAgeGroupByName(PSession, Filters["ageGroupName"]).id # Get the id of the age group
        del Filters["ageGroupName"]                                                         # Delete the name from the filters dict 

    if "sjlName" in Filters:                                                                # If sjlName is given as filter  
        Filters["playerId"] = readOnePlayerByName(PSession, Filters["sjlName"]).id          # Get the id of the player
        del Filters["sjlName"]                                                              # Delete the name from the filters dict

def filterGoalieSeasonLevels(PSession: Session, GoalieSeasonLevels: list, Filters: dict) -> None:
    """
    Queries the database and appends all matching GoalieSeasonLevel rows to the GoalieSeasonLevels list.
    
    Args:
        PSession (Session): The SQLAlchemy session to use for the query.
        GoalieSeasonLevels (list): The list to append the matching rows to.
        Filters (dict): The dictionary of filters to apply to the query.
                         The keys are the names of columns in the goalie_season_levels table, and the values are the values to filter by.
    """
    
    Query = PSession.query(GoalieSeasonLevel)   # Create the empty query object

    if Filters:
        for key, value in Filters.items():      # Loop over keys and values in the filters dict
            Query = Query.filter(getattr(GoalieSeasonLevel, key) == value) # Add a filter to the query                     
    
    # Execute the query and append the results to PlayerSeasonLevels
    Result = Query.all()
    
    for SeasonLevel in Result:
    # Write the custom names to each SeasonLevel object. This is needed for the pydantic model
    # The functions used are from the same module, and return the whole row.
    # Thats why we use ".clubName" for example, to just acces the desired name, not the object itself.
        SeasonLevel.clubName = readOneClubById(PSession, SeasonLevel.clubId).clubName 
        SeasonLevel.levelName = readOneLevelById(PSession, SeasonLevel.levelId).levelName
        SeasonLevel.ageGroupName = readOneAgeGroupById(PSession, SeasonLevel.ageGroupId).ageGroupName

    GoalieSeasonLevels.extend(Result)

    return None

def filterPlayerSeasonLevels(PSession: Session, PlayerSeasonLevels: list, Filters: dict) -> None:
    """
    Queries the database and appends all matching PlayerSeasonLevel rows to the PlayerSeasonLevels list.
    
    Args:
        PSession (Session): The SQLAlchemy session to use for the query.
        PlayerSeasonLevels (list): The list to append the matching rows to.
        Filters (dict): The dictionary of filters to apply to the query.
                         The keys are the names of columns in the player_season_levels table, and the values are the values to filter by.
    """
    
    Query = PSession.query(PlayerSeasonLevel)   # Create the empty query object

    if Filters:
        for key, value in Filters.items():      # Loop over keys and values in the filters dict
            Query = Query.filter(getattr(PlayerSeasonLevel, key) == value) # Add a filter to the query                     
    
    # Execute the query and append the results to PlayerSeasonLevels
    Result = Query.all()
    
    for SeasonLevel in Result:
    # Write the custom names to each SeasonLevel object. This is needed for the pydantic model
    # The functions used are from the same module, and return the whole row.
    # Thats why we use ".clubName" for example, to just acces the desired name, not the object itself.
        SeasonLevel.clubName = readOneClubById(PSession, SeasonLevel.clubId).clubName 
        SeasonLevel.levelName = readOneLevelById(PSession, SeasonLevel.levelId).levelName
        SeasonLevel.ageGroupName = readOneAgeGroupById(PSession, SeasonLevel.ageGroupId).ageGroupName
        
    PlayerSeasonLevels.extend(Result)

    return None

def readPlayersSeasons(PSession: Session, playerId: int, Position: str = None) -> list:
    """
    Queries the database and returns all Seasons for the player with the given id.
    Args: 
        PSession (object): The SQLAlchemy session to use for the query.
        playerId (int): The id of the player to read.
        Position (str): The position of the player, either "Maalivahti", "Hyökkääjä", "Puolustaja" or "Kenttäpelaaja".
    """
    if Position is None:                                                  # In case a Position is not provided in call (as should)
        PlayerRow = PSession.query(Player).filter_by(id=playerId).first() # Query the database to find the player row
        if PlayerRow is None:                                             # If its not found then something is wrong
            raise Exception("Player not found!")                          # Raise an exception

    Position = PlayerRow.position                                         # Get the player's position from the actual player row

    if Position == "Maalivahti":                                          # If the player is a goalie, return all GoalieSeason objects that match the player id
        return PSession.query(GoalieSeason).filter_by(playerId=playerId).all()
    else:                                                                 # Else return all PlayerSeason objects that match the player id
        return PSession.query(PlayerSeason).filter_by(playerId=playerId).all()

def readLevelsForSeason(PSession: Session, PseasonId: int, Position: str = None) -> list:
    """
    Queries the database and returns all SeasonLevels for the given playerSeasonId.
    It also writes custom .clubName, .leveName and .ageGroupName attributes to the SeasonLevel objects.
    These are needed for the pydantic model.
    
    Args:
        PSession (object): The SQLAlchemy session to use for the query.
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
        SeasonLevels = PSession.query(GoalieSeasonLevel).filter_by(seasonId=PseasonId).all()     # Finds all the goalieSeasonLevel rows that match the Season rows id
    else:
        SeasonLevels = PSession.query(PlayerSeasonLevel).filter_by(seasonId=PseasonId).all()     # Finds all the playerSeasonLevel rows that match the Season rows id

    for SeasonLevel in SeasonLevels:
        # Write the custom names to each SeasonLevel object. This is needed for the pydantic model
        # The functions used are from the same module, and return the whole row.
        # Thats why we use ".clubName" for example, to just acces the desired name, not the object itself.
        SeasonLevel.clubName = readOneClubById(PSession, SeasonLevel.clubId).clubName 
        SeasonLevel.levelName = readOneLevelById(PSession, SeasonLevel.levelId).levelName
        SeasonLevel.ageGroupName = readOneAgeGroupById(PSession, SeasonLevel.ageGroupId).ageGroupName
    
    return SeasonLevels # Return the list of seasonsLevel rows with new custom attributes.

def readAllPlayers(PSession: Session) -> list:
    """
    Queries the database and returns all contents of the "players" table. Return just the basic info, no seasons.
    """
    return PSession.query(Player).all()

def parsePlayersToDict(Players: list) -> dict:
    """
    Parses the list of Player objects into a dictionary with the sjlName as the key and the Player object as the value. No seasons.
    """
    PlayersDict = {}
    for Player in Players:
        PlayersDict[Player.sjlName] = Player
    return PlayersDict

def getAllClubs(PSession: Session) -> list:
    """
    Queries the database and returns all contents of the "clubs" table.
    """
    return PSession.query(Club).all()

def parseClubsToDict(Clubs: list) -> dict:
    """
    Parses the list of Club objects into a dictionary with the clubName as the key and the Club object as the value.
    """
    ClubsDict = {}
    for Club in Clubs:
        ClubsDict[Club.clubName] = Club
    return ClubsDict

def getAllLevels(PSession: Session) -> list:
    """
    Queries the database and returns all contents of the "levels" table.
    """
    return PSession.query(Level).all()

def parseLevelsToDict(Levels: list) -> dict:
    """
    Parses the list of Level objects into a dictionary with the levelName as the key and the Level object as the value.
    """
    LevelsDict = {}
    for Level in Levels:
        LevelsDict[Level.levelName] = Level
    return LevelsDict

def getAllAgeGroups(PSession: Session) -> list:
    """
    Queries the database and returns all contents of the "age_groups" table.
    """
    return PSession.query(AgeGroup).all()

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
