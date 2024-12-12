from database.reader import readAllPlayers, parsePlayersToDict, readOnePlayerById, readPlayersSeasons, readLevelsForSeason, convertNamesToIds, filterGoalieSeasonLevels, filterPlayerSeasonLevels
from database.connection import SessionLocal
from api.models import seasonLevelResponse

def getAllPlayers():
    """
    Queries the database and returns a dictionary of all players in the database.
    
    Returns a dictionary with the following structure:
    {
        "Player1 sjlName": Player1 (Player object (Base)),
        "Player2 sjlName": Player2 (Player object (Base)),
        ...
    }
    Each Player object has the following attributes:
    - sjlName (str): The player's name in the format "LASTNAME Firstname".
    - epName (str): The player's name in the format "Firstname Lastname".
    - sjlLink (str): A link to the player's page on the SJL website.
    - birthYear (int): The player's birth year.
    - position (str): The player's position, either "Maalivahti", "Kenttäpelaaja", "Hyökkääjä" or "Puolustaja".
    """
    
    Session = SessionLocal()                    # Create Session object to communicate with SQL Alchemy
    players = readAllPlayers(Session)           # Read all players from the database using the database.readers function
    parsedPlayers = parsePlayersToDict(players) # Parse the list of all Player objects into a dictionary
    return parsedPlayers

def getOnePlayer(id: int):

    """
    Queries the database and returns one player by id.
    
    Args:
        id (int): The id of the player to read.
    
    Returns:
        Player: The player object read from the database.
        Each player object has custom made "seasons" attribute, which is a list containing the seasons for the player.
        Each season object has custom made "seasonLevels" attribute, which is a list containing the seasonLevel objects for the season.

    """
    
    Session = SessionLocal()                                            # Create Session object to communicate with SQL Alchemy
    Player = readOnePlayerById(Session, id)                             # Read the player from the database using the database.readers function
    Player.seasons = readPlayersSeasons(Session, id)                    # Read the seasons for the player from the database. Write this list to the player object .seasons attribute

    for season in Player.seasons:                           
        season.seasonLevels = readLevelsForSeason(Session, season.id, Player.position)   # Read the seasonLevels for the season from the database. Write this list to the season object .seasonLevels attribute
    
        for seasonLevel in season.seasonLevels:
            print(type(seasonLevel))
            print(seasonLevel)
            print("")    
    
    return Player                                                       # Return player object, that has custom .seasons attribute.
                                                                        # List contains season objects, that has custom .seasonLevels attribute containing seasonLevel objects

def getFilteredSeasonLevels(Filters: dict):
    """
    Filters and retrieves season level data based on the provided criteria.

    This function takes a dictionary of filters and queries the database to retrieve
    the matching season level data, which is categorized into goalie and player season levels.
    The function converts certain name-based filters to ID-based filters and applies them
    to the appropriate database tables. It returns a response model containing the lists
    of filtered goalie and player season levels.

    Args:
        Filters (dict): A dictionary containing the filter criteria for querying season levels.
                        Acceptable keys include "position", "clubName", "levelName", "ageGroupName", 
                        "sjlName", "year", "clubId", "levelId", "ageGroupId", "seasonId", "playerId".

    Returns:
        seasonLevelResponse: An object containing lists of filtered goalie and player season levels.

    Raises:
        ValueError: If an unsupported position filter is provided.
    """

    # The original filters contains all query options, so we remove all key-values that are None. This is done because we don't want to add None values to the query.
    FiltersToUse = {}                           # Dict to store the filters to use
    for key, value in Filters.items():          # Iterate over the filters given in the request
        if value is not None:                   # Check if the value is not None, aka contains an actualy query
            FiltersToUse[key] = value           # Add the key-value pair to the FiltersToUse dict
    
    Session = SessionLocal()                    # Create Session object to communicate with SQL Alchemy
    convertNamesToIds(FiltersToUse, Session)    # If there are "clubName", "levelName", "ageGroupName" or "sjlName" in the filters, convert them to "clubId", "levelId", "ageGroupId" or "playerId"
                                                # This is done because the seasonLevel tables dont have the string name values. Therefore we have to use the ids instead.

    # Initialize empty lists to store the seasonLevel objects.
    GoalieSeasonLevels = []
    PlayerSeasonLevels = []

    # Filter the SeasonLevel objects based on the position. This needs to be done separately for the goalie and player season levels, because they have different models both in database and api.
    if FiltersToUse.get("position") == "Maalivahti":                                    # If position in maalivahti.
        del FiltersToUse["position"]                                                    # Remove from filters because its not a key in the "goalie_season_levels" table. Would cause error otherwise.
        filterGoalieSeasonLevels(Session, GoalieSeasonLevels, FiltersToUse)             # Filter goalie season levels. This appends the filtered goalie season level objects to the GoalieSeasonLevels list in place.
    
    elif FiltersToUse.get("position") in ["Kenttäpelaaja", "Puolustaja", "Hyökkääjä"]:  # If position in kenttäpelaaja, puolustaja or hyökkääjä
        del FiltersToUse["position"]                                                    # Remove from filters because its not a key in the "player_season_levels" table. Would cause error otherwise.
        filterPlayerSeasonLevels(Session, PlayerSeasonLevels, FiltersToUse)             # Filter player season levels. This appends the filtered player season level objects to the PlayerSeasonLevels list in place.
    
    elif FiltersToUse.get("position") is None:                                          # If there is no position filter, we need to separately filter goalie and player season level tables.
        filterGoalieSeasonLevels(Session, GoalieSeasonLevels, FiltersToUse)             
        filterPlayerSeasonLevels(Session, PlayerSeasonLevels, FiltersToUse)
    else:                                                                               # If there is a position query filter, but its invalid raise ValueError.
        raise ValueError(f"Unsupported position: {FiltersToUse.get('position')} in getFilteredSeasonLevels")
        

    # We create and return a seaonLevelResponse object, this contains "goalies" and "players" attributes. Both are a list of corresponding seasonLevel objects. 
    Response = seasonLevelResponse()
    Response.goalies = GoalieSeasonLevels
    Response.players = PlayerSeasonLevels

    return Response
    