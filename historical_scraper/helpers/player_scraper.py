from bs4 import BeautifulSoup
import sys
from historical_scraper.models.player import Player
from historical_scraper.models.season import GoalieSeason, PlayerSeason, GoalieSeasonLevel, PlayerSeasonLevel
from historical_scraper.config import CURRENT_YEAR
from historical_scraper.helpers.utils import getSeasonsToScrape, parsePosition, parsePersonalDetails, parseAgeGroupLevelAndClub, parseSeasonAllGoalieStas, parseGoalieStats, parseSeasonAllPlayerStas, parsePlayerStats


def fetchPlayerCareerData(PPlayerLink: str, PPlayerObject: Player, PPage: object) -> dict:
    """
    Fetches the player CAREER data for a given player link and stores it in a provided dictionary.

    This function takes a player link, a dictionary to store the player data in, and a Page object as inputs.
    It opens a browser, goes to the player page, waits for dynamic content to load, and then fetches the player's personal details and position.
    It then fetches the player's season stats for each season they played in and stores them in the provided dictionary.

    Args:
        PPlayerLink (str): The link to the player's page.
        PlayerDataDict (dict): The dictionary to store the player data in.
        PPage (object): The Page object to use.

    Returns:
        dict: The dictionary with the player data, containing the player's personal details, position and season stats.
    """
    print(f"\nScraping player: {PPlayerObject.sjlName}")

    # Open a browser and go to the desired player page
    PPage.goto(PPlayerLink)

    # Wait for one second to load dynamic content
    PPage.wait_for_timeout(00)

    # Get the Html containing the personal details
    PPage.wait_for_selector(".pcm-basic-col", timeout=5000)                 # Wait for it to load
    PersonalDetailsHtml = PPage.locator(".pcm-basic-col").inner_html()      # Personal details are only scraped once per player
    PersonalDetails = parsePersonalDetails(PersonalDetailsHtml)             # Parse the personal details into a dict
    PPlayerObject.birthYear = PersonalDetails["DateOfBirth"]                # Add the date of birth to the player object. Potentially add more personal details later

    # Get the Html containing the player's position
    try:
        PPage.wait_for_selector("td.person-position", timeout=5000)         # Wait for it to load
        PositionHtml = PPage.locator("td.person-position").inner_html()     # Scrape the position info for player
        Position = parsePosition(PositionHtml)                              # Parse the position into a string
        PPlayerObject.position = Position                                   # Add the position to the player object for player
    except:
        # This is a player that is no more active, so sjl displays the information differently.
        print(f"Failed to scrape {PPlayerObject.sjlName}. He hasn't played in the current year.\nResortin to using fetchRetiredPlayerCareerData")
        fetchRetiredPlayerCareerData(PPlayerLink, PPlayerObject, PPage)     # This function does its best to handle the case, and still record all available data.
        return None                                                         # Terminate the regular scraping. 

    scrapeSeasonsForPlayer(PPlayerObject, PPage)                            # Scrape the player's seasons. Outcome Player.seasons <- SeasonObject.seasonLeveStats <- SeasonLevelObject


    return None

def fetchPlayerSeasonHtml(PPage: object, PSeason: str, PPosition: str) -> dict:
    """
    Fetches and parses the player's ONE SEASON statistics from the webpage.

    Args:
        PPage (object): The page object representing the player's webpage.
        PSeason (str): The season for which the stats are to be fetched.
        PPosition (str): The position of the player, either "Maalivahti" (goalie) or "Kenttäpelaaja" (skater).

    Returns:
        dict: A dictionary containing the parsed season statistics. For goalies, it includes "SeasonAllGoalieStas" (dict) and "GoalieLevelStats" (list of dicts). For skaters, it includes "SeasonAllPlayerStas" (dict) and "PlayerLevelStats" (list of dicts).
    """

    # print(f"\n\nFetching stats for season {PSeason}\n")

    # Select season and wait for a second for the content to laod
    PPage.locator("select#pcss-season-select").select_option(PSeason)
    PPage.wait_for_timeout(500)
    
    if PPosition == "Maalivahti":
        SeasonAllStatsHtml = PPage.locator("#pcm-all-stats-container").inner_html()                 # Total stats for Goalie THIS SEASON
        SeasonAllStats = parseSeasonAllGoalieStas(SeasonAllStatsHtml)                               # Parse the total stats into a dict
        
        if len(SeasonAllStats) == 0:                                                                # Try and make sure we dont miss any stats
            print("SOS SeasonAllStats wrong")                                                       # Hopefully exit with some information
            print(SeasonAllStatsHtml)
            print(SeasonAllStats)
            sys.exit(1)

        GoalieLevelStats = []
        Attempts = 0
        while GoalieLevelStats == [] and Attempts < 30:
            GoalieStatsHtml = PPage.locator("#pcss-goalie-serie-stats-series-container").inner_html()   # Goalie stats per league THIS SEASON
            GoalieLevelStats = parseGoalieStats(GoalieStatsHtml)                                        # Parse the goalie stats into a dict
            PPage.wait_for_timeout(100)                                                                 # Wait for 100ms
            Attempts += 1                                                                               # After 15 attempts, give up.

        # If the goalie stats are empty, set the goalie stats to "0"
        if GoalieLevelStats == {}:
            SeasonAllStats = {"Games": "0", "Played": "0", "GoalsAllowed": "0", "TimeOnIce": "0", "Gaa": "0"}

        # Store the total stats and goalie stats in a dict
        RawHtml = {"SeasonAllGoalieStas": SeasonAllStats, "GoalieLevelStats": GoalieLevelStats}   

    else: # Position is "Kenttäpelaaja" aka player
        SeasonAllStatsHtml = PPage.locator("#psac-all-skater-stats-container").inner_html()         # Total stats for Player THIS SEASON
        SeasonAllStats = parseSeasonAllPlayerStas(SeasonAllStatsHtml)                               # Parse the total stats into a dict

        if len(SeasonAllStats) == 0:                                                                # Try and make sure we dont miss any stats
            print("SOS SeasonAllStats wrong")                                                       # Hopefully exit with some information
            print(SeasonAllStatsHtml)
            print(SeasonAllStats)
            sys.exit(1)

        PlayerLevelStats = []
        Attempts = 0
        while PlayerLevelStats == [] and Attempts < 15:
            PlayerStatsHtml = PPage.locator("#pcss-skater-serie-stats-series-container").inner_html()   # Player stats per league THIS SEASON
            PlayerLevelStats = parsePlayerStats(PlayerStatsHtml)                                        # Parse the player stats into a dict
            PPage.wait_for_timeout(100)                                                                 # Wait for 100ms
            Attempts += 1                                                                               # After 15 attempts, give up.

        # If the player stats are empty, set the player stats to "0"
        if PlayerLevelStats == []:
            SeasonAllStats = {"Games": "0", "Goals": "0", "Assists": "0", "Points": "0", "PenaltyMinutes": "0", "PpGoals": "0", "ShGoals": "0", "SoGoals": "0"}

        # Store the total stats and player stats in a dict
        RawHtml = {"SeasonAllPlayerStas": SeasonAllStats, "PlayerLevelStats": PlayerLevelStats}
        
    return RawHtml

def scrapeSeasonsForPlayer(PPlayerObject: Player, PPage: object):
    """
    Scrapes the player's stats for all seasons in the list obtained from getSeasonsToScrape and stores them in the player object.
    Based on the position of the player either scrape goalie or player data.
    For each season create a Season object and add it to the player object.
    For each level per seasons create a Level object and add it to the Season object.

    Args:
        PPlayerObject (Player): The player object to store the scraped data in.
        PPage (object): The Page object to use. Must be loaded with the player page.

    Returns:
        None
    """
    # This gets the seasons to scrape based on birth year. Returns a list of years as strings ["2025", "2024", "2023"...]
    SeasonsToScrape = getSeasonsToScrape(PPlayerObject.birthYear)       

    # Get the Html containing the player's season stats
    for Season in SeasonsToScrape:
        StatsDict = fetchPlayerSeasonHtml(PPage, Season, PPlayerObject.position)  # Fetch the player's season stats. It is stored in dict.
        
        if PPlayerObject.position == "Maalivahti":
            SeasonObject = GoalieSeason(Season, StatsDict["SeasonAllGoalieStas"])   # Here we create a object to represent the whole season
            PPlayerObject.addSeason(SeasonObject)                                   # Add the season object to the player object.seasons
            for Level in StatsDict["GoalieLevelStats"]:                             # Iterate over all the levels in the season
                SeasonLevelObject = GoalieSeasonLevel(Level)                        # Create a object to represent the games they played on one season at this level
                SeasonObject.addLevelStat(SeasonLevelObject)                        # Add the level object to the season object.seasonLevelStats


        else: # If position is "Kenttäpelaaja"
            SeasonObject = PlayerSeason(Season, StatsDict["SeasonAllPlayerStas"])   # Create a object to represent the whole season
            PPlayerObject.addSeason(SeasonObject)                                   # Add the season object to the player object.seasons
            for Level in StatsDict["PlayerLevelStats"]:                             # Iterate over all the levels in the season
                SeasonLevelObject = PlayerSeasonLevel(Level)                        # Create a object to represent the games they played on one season at this level
                SeasonObject.addLevelStat(SeasonLevelObject)                        # Add the level object to the season object.seasonLevelStats

def writeSeasonLevelDetails(PPlayersDict: dict) -> None:
    """
    Writes the age group, level and club from the player's season level stats to the console.
    
    Args:
        PPlayersDict (dict): A dictionary of Player objects.

    Returns:
        None
    """
    # NameKey is the a key in the dict that is the name of the player "JOKUNEN Jaska"
    # Player is the player object that is the value in the dict
    for NameKey, Player in PPlayersDict.items():
        print(Player.sjlName)
        for season in Player.seasons:
            for LevelStats in season.seasonLevelStats:
                parseAgeGroupLevelAndClub(LevelStats)
                print(LevelStats)

    return None

def fetchRetiredPlayerCareerData(PPlayerLink: str, PPlayerObject: Player, PPage: object) -> dict:
    """
    Fetches the player CAREER data for a given retired player link and stores it in the provided Player object.

    This function takes a player link, a dictionary to store the player data in, and a Page object as inputs.
    It opens a browser, goes to the player page, waits for dynamic content to load, and then fetches the player's personal details and position.
    It then fetches the player's season stats for each season they played in and stores them in the provided dictionary.

    Args:
        PPlayerLink (str): The link to the player's page.
        PlayerDataDict (dict): The dictionary to store the player data in.
        PPage (object): The Page object to use.

    Returns:
        dict: The dictionary with the player data, containing the player's personal details, position and season stats.
    """

    # This gets the last 10 seasons as strings  ["2025", "2024", "2023"...]
    SeasonsToScrape = getSeasonsToScrape("2000") # "2000" because its far enough birthdate to give the full 10 years.
    LastSeasonPlayed = None

    # Try to find the last the seasons the player has still played
    for Season in SeasonsToScrape:
        PPage.locator("select#pcss-season-select").select_option(Season)
        PPage.wait_for_timeout(800)
        SeasonTeamsHtml = PPage.locator("#pcss-player-season-teams").inner_html()
        
        # Since this seasons html contain some data, this is the last season they played.
        if len(SeasonTeamsHtml) > 0:
            print(f"{Season} is the latest {PPlayerObject.sjlName} has played in")
            LastSeasonPlayed = Season

            # Check the position of the player and write it the to the object.position attribute.
            checkRetiredPoistion(PPlayerObject, PPage)

            # Get the birth year for the player (Guess current year - Age )
            PlayerAge = int(PPage.locator("#pcm-player-age").inner_html())
            PlayerBirthYear = CURRENT_YEAR - PlayerAge
            PPlayerObject.birthYear = PlayerBirthYear
            break
    
    # Get the range of seasons to scrape. Last year played - (assumed) U13 season.
    SeasonsToScrape = getSeasonsToScrape(PPlayerObject.birthYear, LastSeasonPlayed)

    # Get the Html containing the player's season stats
    for Season in SeasonsToScrape:
        StatsDict = fetchPlayerSeasonHtml(PPage, Season, PPlayerObject.position)  # Fetch the player's season stats. It is stored in dict.
        
        if PPlayerObject.position == "Maalivahti":
            print(f"{Season} SeasonAllGoalieStas: {StatsDict["SeasonAllGoalieStas"]}")
            SeasonObject = GoalieSeason(Season, StatsDict["SeasonAllGoalieStas"])
            for Level in StatsDict["GoalieLevelStats"]:   # DEBUG PRINT
                print(f"{Level}")
            # PlayerDataDict[Season] = StatsDict
            PPlayerObject.addSeason(SeasonObject)

        else: # If position is "Kenttäpelaaja"
            print(f"{Season} SeasonAllPlayerStas: {StatsDict["SeasonAllPlayerStas"]}")
            for Level in StatsDict["PlayerLevelStats"]:   # DEBUG PRINT
                print(f"{Level}")
            # PlayerDataDict[Season] = StatsDict
            SeasonObject = PlayerSeason(Season, StatsDict["SeasonAllPlayerStas"])
            PPlayerObject.addSeason(SeasonObject)


    return None

def checkRetiredPoistion(PPlayerObject: Player, PPage: object) -> None:
    """
    Checks the position of a player from the player page and sets the position field of PPlayerObject accordingly.

    Args:
        PPlayerObject (Player): The player object to set the position for.
        PPage (object): The Page object to use. Must be loaded with the player page.

    Returns:
        None
    """
    GoalieDiv = PPage.locator("#psac-all-goalie-stats-container")
    PlayerDiv = PPage.locator("#psac-all-skater-stats-container")

    # Player is a goalie
    if GoalieDiv.is_visible():
        print(f"{PPlayerObject.sjlName} is a goalie")
        PPlayerObject.position = "Maalivahti"            

    # Player is a skater
    if PlayerDiv.is_visible():
        print(f"{PPlayerObject.sjlName} is a skater")
        PPlayerObject.position = "Kenttäpelaaja"

    # Player is not a goalie or skater
    if not GoalieDiv.is_visible() and not PlayerDiv.is_visible():
        print(f"{PPlayerObject.sjlName} is not a goalie or skater")
        sys.exit(1)

    if GoalieDiv.is_visible() and PlayerDiv.is_visible():
        print(f"{PPlayerObject.sjlName} is a goalie and skater")
        sys.exit(1)

    return None