from database.connection import SessionLocal
from database.models import Player, Club, Level, AgeGroup

def readAllPlayers(Session: object) -> list:
    """
    Queries the database and returns all contents of the "players" table.
    """
    return Session.query(Player).all()

def parsePlayersToDict(Players: list) -> dict:
    """
    Parses the list of Player objects into a dictionary with the sjlName as the key and the Player object as the value.
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

