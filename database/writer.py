

from database.connection import SessionLocal
from database.models import Player as PlayerRow, GoalieSeason as GoalieSeasonRow, PlayerSeason as PlayerSeasonRow, PlayerSeasonLevel as PlayerSeasonLevelRow, GoalieSeasonLevel as GoalieSeasonLevelRow, Club as ClubRow, Level as LevelRow, AgeGroup as AgeGroupRow
from historical_scraper.models.player import Player as PlayerObject
from database.converters import playerConverter, goalieSeasonConverter, playerSeasonConverter, playerSeasonLevelConverter, goalieSeasonLevelConverter, createClubRow, createLevelRow, createAgeGroupRow

def checkIfClubExists(ClubName: str, Session: object) -> int:
    """
    Checks if a club row with the given ClubName already exists in the "clubs" table.
    If it exists, return the id.
    If not, create a new row and return the id.

    Args:
        ClubName (str): The name of the club to check.
        Session (object): The SQLAlchemy session to use for the query.

    Returns:
        int: The id of the club row if it already exists, or the id of a newly created club row if it doesn't exist yet.
    """
    try:
        Row = Session.query(ClubRow).filter(ClubRow.clubName == ClubName).one() # Try finding the row with the given ClubName 
        return Row.id                                                           # If found, return the id
    except Exception:
        Club = createClubRow(ClubName)                                          # If its not found create a new row
        Session.add(Club)                                                       # Add the new row to the session
        Session.flush()                                                         # Flush the changes to get thd ID
        print(f"\nCreated a new club row for {ClubName}\n")                     # Print for improved readability
        return Club.id                                                          # Return the id
    
def checkIfLevelExists(LevelName: str, Session: object) -> int:
    """
    Checks if a level row with the given LevelName already exists in the "levels" table.
    If it exists, return the id.
    If not, create a new row and return the id.

    Args:
        LevelName (str): The name of the level to check.
        Session (object): The SQLAlchemy session to use for the query.

    Returns:
        int: The id of the level row if it already exists, or the id of a newly created level row if it doesn't exist yet.
    """
    try:
        Row = Session.query(LevelRow).filter(LevelRow.levelName == LevelName).one() # Try finding the row with the given LevelName
        return Row.id                                                               # If found, return the id
    except Exception:
        Level = createLevelRow(LevelName)                                           # If its not found create a new row
        Session.add(Level)                                                          # Add the new row to the session
        Session.flush()                                                             # Flush the changes to get thd ID
        print(f"\nCreated a new level row for {LevelName}\n")                       # Print for improved readability
        return Level.id                                                             # Return the id
    
def checkIfAgeGroupExists(AgeGroupName: str, Session: object) -> int:
    """
    Checks if an age group row with the given AgeGroupName already exists in the "age_groups" table.
    If it exists, return the id.
    If not, create a new row and return the id.

    Args:
        AgeGroupName (str): The name of the age group to check.
        Session (object): The SQLAlchemy session to use for the query.

    Returns:
        int: The id of the age group row if it already exists, or the id of a newly created age group row if it doesn't exist yet.
    """

    try:
        Row = Session.query(AgeGroupRow).filter(AgeGroupRow.ageGroupName == AgeGroupName).one() # Try finding the row with the given AgeGroupName
        return Row.id                                                                           # If found, return the id
    except Exception:
        AgeGroup = createAgeGroupRow(AgeGroupName)                                              # If its not found create a new row
        Session.add(AgeGroup)                                                                   # Add the new row to the session
        Session.flush()                                                                         # Flush the changes to get thd ID
        print(f"\nCreated a new age group row for {AgeGroupName}\n")                            # Print for improved readability
        return AgeGroup.id                                                                      # Return the id



def writePlayerToDb(PlayerRow: PlayerRow, Session: object) -> int:
        
    """
    Writes a PlayerRow to the database using the given Session.
    
    Args:
        PlayerRow (PlayerRow): The row to write to the database.
        Session (object): The SQLAlchemy session to use for the query.
    
    Returns:
        int: The id of the newly created row. Used to link other rows (Seasons / LevelSeasons) to this one.
    """
    Session.add(PlayerRow)
    Session.flush()
    return PlayerRow.id

def writeSeasonToDb(Season: object, PlayerId: int, Position: str, Session: object) -> int:    
    """
    Writes a Season to the database using the given Session.
    One Seasons represents one players Combined stats for one year.
    If the player is a goalie, a goalieSeason is created.
    If the player is a player, a playerSeason is created.
    
    Args:
        Season (object): The season to write to the database.
        PlayerId (int): The id of the player row in the players table to link the season to.
        Position (str): The position of the player, either "Maalivahti" or "Kenttäpelaaja".
        Session (object): The SQLAlchemy session to use for the query.
    
    Returns:
        int: The id of the newly created row. Used to link other rows (LevelSeasons) to this one.
    """
    if Position == "Maalivahti":            
        SeasonRow = goalieSeasonConverter(Season, PlayerId) # This converts the Season object (from scraping) to a goalieSeasonRow (Base, used in SQL Alchemy)
    elif Position == "Kenttäpelaaja":
        SeasonRow = playerSeasonConverter(Season, PlayerId) # This converts the Season object (from scraping) to a playerSeasonRow (Base, used in SQL Alchemy)
    else:
        raise ValueError(f"Unsupported position: {Position} in writeSeasonToDb")    # Just in case the position is not supported

    Session.add(SeasonRow)
    Session.flush()
    return SeasonRow.id

def writeSeasonLevelToDb(SeasonLevelObject: object, SeasonId: int, PlayerObject: object, Session: object) -> None:
    """
    Writes a SeasonLevelStat to the database using the given Session.
    Checks if club, level and ageGroup are already on their respective tables. If not, first creates those rows.
    A SeasonLevelStat is part of a Season and contains the stats for one ("U16 AAA" or "U18 SM" or "U18 Mestis" for example) level in that season.

    Args:
        SeasonLevelObject (object): The SeasonLevelStat to write to the database. This is a scraped seasonLevelObject
        SeasonId (int): The id of the season row in the goalie_seasons or player_seasons table to link the level to.
        PlayerObject (object): The PlayerObject from which the SeasonLevelStat was created. Needed to determine the correct position.
        Session (object): The SQLAlchemy session to use for the query.
    """
    clubId = checkIfClubExists(SeasonLevelObject.club, Session)             # Checks if the club exists in the clubs table. If not, creates a new row. Return ID.
    levelId = checkIfLevelExists(SeasonLevelObject.level, Session)          # Checks if the level exists in the levels table. If not, creates a new row. Return ID.
    ageGroupId = checkIfAgeGroupExists(SeasonLevelObject.ageGroup, Session) # Checks if the ageGroup exists in the age_groups table. If not, creates a new row. Return ID.
    
    if PlayerObject.position == "Maalivahti":
        SeasonLevelStatRow = goalieSeasonLevelConverter(SeasonLevelObject, SeasonId, clubId, levelId, ageGroupId, PlayerObject.id)  # This converts the goalieSeasonLevelObject (from scraping) to a goalieSeasonLevelRow (Base, used in SQL Alchemy) 
    elif PlayerObject.position == "Kenttäpelaaja":
        SeasonLevelStatRow = playerSeasonLevelConverter(SeasonLevelObject, SeasonId, clubId, levelId, ageGroupId, PlayerObject.id)  # This converts the playerSeasonLevelObject (from scraping) to a playerSeasonLevelRow (Base, used in SQL Alchemy) 
    else:
        raise ValueError(f"Unsupported position: {PlayerObject.position} in writeSeasonLevelToDb")  # Just in case the position is not supported

    Session.add(SeasonLevelStatRow)
    Session.flush()

def writeEntirePlayerToDb(PlayerObject: PlayerObject) -> None:
    """
    This function takes a PlayerObject as input and writes it to the database.

    1. Create a session to use for writing
    2. Convert the PlayerObject to a PlayerRow
    3. Write the PlayerRow to the database
    4. For each Season in the PlayerObject, write the Season to the database
    5. For each SeasonLevelStat in the Season, write the SeasonLevelStat to the database
    5a. Also create new club, level and ageGroup rows if needed.

    Args:
        PlayerObject (PlayerObject): The player to write to the database. This is a scraped player object

    Returns:
        None
    """
    Session = SessionLocal()                        # Create the session to use for all rows
    PlayerRow = playerConverter(PlayerObject)       # Convert the PlayerObject to a PlayerRow (Base), this can be written to table with SQLAlchemy
    PlayerId = writePlayerToDb(PlayerRow, Session)  # Write the PlayerRow to the database "players" table, return the ID
    PlayerObject.id = PlayerId                      # Assign the ID to the PlayerObject

    for key, value in vars(PlayerObject).items():   # Print all the attributes of the PlayerObject for debugging
        print(f"{key}: {value}")

    for Season in PlayerObject.seasons:
        SeasonId = writeSeasonToDb(Season, PlayerId, PlayerObject.position, Session)    # Write the Season to the database and return the ID

        for SeasonLevelStat in Season.seasonLevelStats:
            writeSeasonLevelToDb(SeasonLevelStat, SeasonId, PlayerObject, Session)      # Write the SeasonLevelStat to the database


    Session.commit()
    Session.close()
