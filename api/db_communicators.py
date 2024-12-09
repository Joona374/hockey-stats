from database.reader import readAllPlayers, parsePlayersToDict, readOnePlayer, readPlayersSeasons, readLevelsForSeason
from database.connection import SessionLocal

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
    Player = readOnePlayer(Session, id)                                 # Read the player from the database using the database.readers function
    Player.seasons = readPlayersSeasons(Session, id)                    # Read the seasons for the player from the database. Write this list to the player object .seasons attribute
    for season in Player.seasons:                           
        season.seasonLevels = readLevelsForSeason(Session, season.id, Player.position)   # Read the seasonLevels for the season from the database. Write this list to the season object .seasonLevels attribute
    return Player                                                       # Return player object, that has custom .seasons attribute.
                                                                        # List contains season objects, that has custom .seasonLevels attribute containing seasonLevel objects