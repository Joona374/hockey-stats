from playwright.sync_api import sync_playwright

from database.reader import getSeasonObjectsByYear, getAllPlayerObjects, getAllGoalieObjects, getSeasonLevelsForGoalieSeason, getSeasonLevelsForPlayerSeason, readOneLevelById, readOneAgeGroupById, readOneClubByName, readOneAgeGroupByName, readOneLevelByName
from database.connection import SessionLocal
from database.models import GoalieSeasonLevel as GoalieSeasonLevelRow, PlayerSeasonLevel as PlayerSeasonLevelRow, GoalieSeason as GoalieSeasonRow, PlayerSeason as PlayerSeasonRow
from database.converters import goalieSeasonLevelConverter, playerSeasonLevelConverter

from historical_scraper.helpers.player_scraper import fetchPlayerSeasonHtml
from historical_scraper.helpers.utils import parseAgeGroupLevelAndClub
from historical_scraper.models.season import GoalieSeasonLevel as GoalieSeasonLevelObject, PlayerSeasonLevel as PlayerSeasonLevelObject


from .config import CURRENT_YEAR
from .helpers import goaliesToDict, playersToDict

def goToSeasonPlayerPage(Page: object, PlayersDict: dict, SeasonRow: object) -> None:
    """
    Navigates to the player's page for a specific season.

    This function takes a Page object, a dictionary of player objects, 
    and a SeasonRow object. It retrieves the player object corresponding 
    to the playerId in the SeasonRow, obtains the player's link, and 
    navigates the Page to the player's SJL page.

    Args:
        Page (object): The Page object used to navigate to the player's page.
        PlayersDict (dict): A dictionary containing player objects, 
                            where keys are playerIds and values are Player objects.
        SeasonRow (object): An object containing season information, 
                            including the playerId for the desired player.

    Returns:
        None
    """

    PlayerObject = PlayersDict[SeasonRow.playerId]  # Get the correct player object from the player dict that matches the playerId in the seasonRow
    PlayerLink = PlayerObject.sjlLink               # Get the player link from the player object
    Page.goto(PlayerLink)                           # Route the page to the players sjl page
    print(f"We scrape and if necessary, update season level rows for {PlayerObject.sjlName}")

def updateGoaliesRow(LevelRow: GoalieSeasonLevelRow, LevelObject: GoalieSeasonLevelObject) -> None:
    """
    This updates the fields of a goalie season level row in the table from the corresponding scraped object that has the latest data.

    Args:
        LevelRow (GoalieSeasonLevelRow): The row object to update in the table.
        LevelObject (GoalieSeasonLevelObject): The scraped object containing the latest goalie season statistics.

    Returns:
        None
    """
    LevelRow.games = LevelObject.games
    LevelRow.played = LevelObject.played
    LevelRow.goalsAllowed = LevelObject.goalsAllowed
    LevelRow.saves = LevelObject.saves
    LevelRow.savePercentage = LevelObject.savePercentage
    print(f"Updated goalie season: {LevelRow}")


def updatePlayersRow(LevelRow: PlayerSeasonLevelRow, LevelObject: PlayerSeasonLevelObject) -> None:
    """
    This updates the fields of a player season level row in the table from the corresponding scraped object that has the latest data.

    Args:
        LevelRow (PlayerSeasonLevelRow): The row object to update in the table.
        LevelObject (PlayerSeasonLevelObject): The scraped object containing the latest player season statistics.

    Returns:
        None
    """
    
    LevelRow.games = LevelObject.games
    LevelRow.goals = LevelObject.goals
    LevelRow.assists = LevelObject.assists
    LevelRow.points = LevelObject.points
    LevelRow.penaltyMinutes = LevelObject.penaltyMinutes


def createGoaliesRow(Session: object, Season: GoalieSeasonRow, LevelObject: GoalieSeasonLevelObject) -> None:
    """
    Creates a new row in the goalie_season_levels table and adds it to the given database session.

    Args:
        Session (object): The database session object to add the row to.
        Season (GoalieSeasonRow): The season row from the table.
        LevelObject (GoalieSeasonLevelObject): The object containing the goalie season statistics.

    Returns:
        None
    """
    ClubId = readOneClubByName(Session, LevelObject.club).id                    # These get the ids of the club, level and age group
    LevelId = readOneLevelByName(Session, LevelObject.level).id                 # They are needed to create the goalie season level row
    AgeGroupId = readOneAgeGroupByName(Session, LevelObject.ageGroup).id        # As the table has a foreign key to the clubs, levels and age groups, not the name values. 

    # This creates the goalie season level row object and adds it to the session. To convert the scraped object, we also need ids for season, club, level, age group and player.
    print(f"Do these containg the player id {LevelObject.playerId}")
    GoalieSeasonLevelRow = goalieSeasonLevelConverter(LevelObject, Season.id, ClubId, LevelId, AgeGroupId, Season.playerId)
    Session.add(GoalieSeasonLevelRow)
    Session.flush()


def createPlayersRow(Session: object, Season: PlayerSeasonRow, LevelObject: PlayerSeasonLevelObject) -> None:
    """
    Creates a new row in the player_season_levels table and adds it to the given database session.

    Args:
        Session (object): The database session object to add the row to.
        Season (PlayerSeasonRow): The season row from the table.
        LevelObject (PlayerSeasonLevelObject): The object containing the player season statistics.

    Returns:
        None
    """
    ClubId = readOneClubByName(Session, LevelObject.club).id                    # These get the ids of the club, level and age group
    LevelId = readOneLevelByName(Session, LevelObject.level).id                 # They are needed to create the player season level row
    AgeGroupId = readOneAgeGroupByName(Session, LevelObject.ageGroup).id        # As the table has a foreign key to the clubs, levels and age groups, not the name values. 

    # This creates the player season level row object and adds it to the session. To convert the scraped object, we also need ids for season, club, level, age group and player.
    PlayerSeasonLevelRow = playerSeasonLevelConverter(LevelObject, Season.id, ClubId, LevelId, AgeGroupId, Season.playerId)
    Session.add(PlayerSeasonLevelRow)
    Session.flush()


def getSeasonLevelsInTable(Session: object, SeasonId: int, Position: str) -> dict[tuple[str, str], object]:
    """
    Retrieves all the season level rows related to the given season id from the database
    and returns them in a dictionary. Keys are tuples of (levelName, ageGroupName)

    Args:
        Session (object): The session object used to interact with the database.
        SeasonId (int): The id of the season for which to retrieve the season level rows.
        Position (str): The position of the player. Either "Maalivahti" or "Kenttäpelaaja".

    Returns:
        dict[tuple[str, str], object]: A dictionary where the keys are tuples of (levelName, ageGroupName)
        and the values are the corresponding season level row objects.
    """
    
    if Position == "Maalivahti":
        SeasonLevelsInTable = getSeasonLevelsForGoalieSeason(Session, SeasonId)               # Get all the season level rows related to this season row
    else:
        SeasonLevelsInTable = getSeasonLevelsForPlayerSeason(Session, SeasonId)               # Get all the season level rows related to this season row

    SeasonLevelsInTableDict = {}                                                          # Init a dict for easier look up
    for SeasonLevel in SeasonLevelsInTable:                                               # Iterate over all the season level rows to add them to the dict
        LevelName = readOneLevelById(Session, SeasonLevel.levelId).levelName              # Get the level name from the level id
        AgeGroupName = readOneAgeGroupById(Session, SeasonLevel.ageGroupId).ageGroupName  # Get the age group name from the age group id
        SeasonLevelsInTableDict[(LevelName, AgeGroupName)] = SeasonLevel                  # Store the season level row in the dict, with key tuple(levelName, ageGroupName)
    SeasonLevelsInTable.clear()                                                           # Clear the list at the end

    return SeasonLevelsInTableDict

def getUpdatedSeasonLevels(Page: object, Position: str) -> list:
    UpdatedSeasonLevels = fetchPlayerSeasonHtml(Page, str(CURRENT_YEAR), Position)  # Scrapes the page for latest data, and formats it into a dict
    UpdatedSeasonLevelObjects = []                                                  # Init a empty list. This is also returned one filled        

    if Position == "Maalivahti":                                                    # Check the position, raise error if need be
        LevelStatsKey = "GoalieLevelStats"                                          # The dict returned above has different keys depending on the position so we need this
    elif Position in ["Kenttäpelaaja", "Hyökkääjä", "Puolustaja"]:                  
        LevelStatsKey = "PlayerLevelStats"
    else:
        raise Exception("Unknown position")

    for seasonsLevel in UpdatedSeasonLevels[LevelStatsKey]:                         # Here each seasonsLevel is a dict containing the scraped season level stats
        if Position == "Maalivahti":                                                # If the position is goalie, we need to convert the dict to a goalie season level object
            SeasonLevelObject = GoalieSeasonLevelObject(seasonsLevel)               # Create a GoalieSeasonLevelObject from the dict for better data handling
        else:                                                                       # Elif a player, we already checked for exceptions above.
            SeasonLevelObject = PlayerSeasonLevelObject(seasonsLevel)               # Same for player, create a PlayerSeasonLevelObject from the dict.
        parseAgeGroupLevelAndClub(SeasonLevelObject)                                # This parses "teamName" eg "Pelicans Turkoosi, Pelicans Valkoinen" in to "club" eg "Pelicans", and splits "levelName" eg "U14 AAA" to "level" eg "U14" and "ageGroup" eg "AAA"
        UpdatedSeasonLevelObjects.append(SeasonLevelObject)                         # Add the newly created object (reprsenting a season level) to the list
    
    return UpdatedSeasonLevelObjects                                                # Return a list containining all the season level objects

def compareOldAndNewData(UpdatedSeasonLevelObjects: list, SeasonLevelsInTableDict: dict, Season: object, Session: object, Position: str) -> None:

    for SeasonLevelObject in UpdatedSeasonLevelObjects:                 # Each SeasonLevelObject is a just scraped season level object
        MatchingRow = SeasonLevelsInTableDict.get((SeasonLevelObject.level, SeasonLevelObject.ageGroup), None)  # This checks if there is a season level row in the table that matches this scraped season level. If age group and level match, the scraped object and row represent the same data.

        if MatchingRow:                                                 # If the scraped object matches a row in the table, we update the row
            if MatchingRow.games != int(SeasonLevelObject.games):       # Check if the number of games is the same in both. This indicates that the scraped data is different from the table, so we need to update it. If they are equal, the player hasnt played any games at this level after last update. In this case no need to do anything.
                print(f"At row {MatchingRow.id} These didnt match: Row in table has {type(MatchingRow.games)}:{MatchingRow.games} and the scraped object has {type(SeasonLevelObject.games)}{SeasonLevelObject.games}")
                if Position == "Maalivahti":
                    updateGoaliesRow(MatchingRow, SeasonLevelObject)    # If the position is goalie, we update the row object with this function
                else:
                    updatePlayersRow(MatchingRow, SeasonLevelObject)    # If the position is player, we update the row object with this function
                Session.flush()                                         # We flush, to "soft save" the updated row to the database

        else:                                                           # If the scraped object does not match a row in the table, it means this a level the player hadnt played before in the season, so we need to create a new row. 
            if Position == "Maalivahti":
                createGoaliesRow(Session, Season, SeasonLevelObject) # If the position is goalie, we create a new row wit this function
            else:
                createPlayersRow(Session, Season, SeasonLevelObject) # If the position is player, we create a new row wit this function
            Session.flush()                                             # We flush, to "soft save" the new row to the database

def updateLatestData() -> None:
    print("Script to update the latest season is live.")

    # 1. We just fetch all the needed data from the database and parse the goalie and player row lists in to dicts for easier look up. 
    Session = SessionLocal()                                            # Create the session to use for this part
    Goalies = getAllGoalieObjects(Session)                              # This is a list of Goalie Row objects
    Players = getAllPlayerObjects(Session)                              # Same for players
                                                                        # We get these mainly to match the Id's to season objects and get player links to scrape
    GoaliesDict = goaliesToDict(Goalies)                                # We convert the goalie list to a dict for easier look up
    PlayersDict = playersToDict(Players)                                # Same for players

    thisYearsSeasons = getSeasonObjectsByYear(Session, CURRENT_YEAR)    # Get all goalie and player season objects for the current year. This is a dict with two keys, "goalies" and "players". Each key contains a list of season objects.

    Session.close()                                                     # Close the session as it not used anymore

    with sync_playwright() as p:
        # 2. Init the browser and page. The same page will be used for all requests, just replacing the url
        Browser = p.chromium.launch(headless=True)
        Page = Browser.new_page()
        Session = SessionLocal()                                        # Create the session to use for this part

        try:
            # 3. We iterate over all the goalies. Each "Season" is a row in goalie-seasons table. 
            for Season in thisYearsSeasons["goalies"]:
                # 4. This takes the Page objects, and redirects it to the player's (who this season belongs to) sjl page                                  
                goToSeasonPlayerPage(Page, GoaliesDict, Season)                         
                
                # 5. These are the data in the table ATM. This returns a dict of all the goalie season level rows in the table for this season. Key is tuple(level, ageGroup) eg. ("AAA", "U15")
                SeasonLevelsInTableDict  = getSeasonLevelsInTable(Session, Season.id, "Maalivahti")   
                
                # 6. These are the new data for the season! This returns a list of all the goalie season level objects for this season. These objects represent the scraped season level data.
                UpdatedSeasonLevelObjects = getUpdatedSeasonLevels(Page, "Maalivahti")

                # 7. Compare the old and new data. Either update the rows or create new ones, if the level is new for the season.   
                compareOldAndNewData(UpdatedSeasonLevelObjects, SeasonLevelsInTableDict, Season, Session, "Maalivahti")


            # 8. Once we are done with goalies, we do the same for players. Each "Season" is a row in player-seasons table.
            for Season in thisYearsSeasons["players"]:
                # 9. This takes the Page objects, and redirects it to the player's (who this season belongs to) sjl page
                goToSeasonPlayerPage(Page, PlayersDict, Season)

                # 10. These are the data in the table ATM. This returns a dict of all the goalie season level rows in the table for this season. Key is tuple(level, ageGroup) eg. ("AAA", "U15")
                SeasonLevelsInTableDict  = getSeasonLevelsInTable(Session, Season.id, "Kenttäpelaaja")

                # 11. These are the new data for the season! This returns a list of all the goalie season level objects for this season. These objects represent the scraped season level data.
                UpdatedSeasonLevelObjects = getUpdatedSeasonLevels(Page, "Kenttäpelaaja")

                # 12. Compare the old and new data. Either update the rows or create new ones, if the level is new for the season.
                compareOldAndNewData(UpdatedSeasonLevelObjects, SeasonLevelsInTableDict, Season, Session, "Kenttäpelaaja")
            
            # 13. Once we are done with both goalies and players, we commit the changes to the database.
            Session.commit()

        except Exception as e:
            Session.rollback()
            print(f"An error occurred: {e}")
        
        finally:
            Session.close()

    return None
    