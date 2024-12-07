from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

import sys

from config import CURRENT_YEAR
from scraper_helpers.classes import Player, GoalieSeason, GoalieSeasonLevel, PlayerSeason, PlayerSeasonLevel

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

def getSeasonsToScrape(PBirthYear: str, LastSeasonActive:str=None) -> list[str]:
    """
    Generates a list of seasons to scrape for a player based on their birth year.

    This function takes the current year and the birth year of the player as inputs and returns a list of seasons to scrape, given as strings in the format "YYYY".

    The function starts from the current year and goes back in time until the difference between the current year and the birth year is less than 13 or until the list has reached a maximum of 10 seasons. This means that if the player was born 13 or more years ago, the function will scrape the last 10 seasons the player was active, and if the player was born less than 13 years ago, the function will scrape all the seasons the player was active.

    Args:
        PBirthYear (str): The birth year of the player.

    Returns:
        list[str]: A list of seasons to scrape, given as strings in the format "YYYY".
    """
    # Get the current season, or if retired player, set current to last year played.
    CurrentSeason = CURRENT_YEAR
    if LastSeasonActive is not None:
        CurrentSeason = int(LastSeasonActive)

    # Convert the birth year to an integer
    BirthYear = int(PBirthYear)

    # Initialize an empty list to store the seasons to scrape
    SeasonsToScrape = []

    # Loop while the difference between the current year and the birth year is less than 13 or the list has reached a maximum of 10 seasons
    while (CurrentSeason - BirthYear >= 13) and len(SeasonsToScrape) < 10:
        # Append the current season to the list
        SeasonsToScrape.append(str(CurrentSeason))
        # Decrement the current season by one
        CurrentSeason -= 1

    # Return the list of seasons to scrape
    return SeasonsToScrape


def parsePosition(PRawHtml: str) -> str:
    """
    Parses the position of a player from the raw HTML of the player page.

    Args:
        PRawHtml (str): The raw HTML of the player page.

    Returns:
        str: The position of the player as a string.
    """
    Soup = BeautifulSoup(PRawHtml, "html.parser")   # Parse the raw HTML
    PositionText = Soup.get_text()                  # Get the text for position
    Position = PositionText.split(" ")[1]           # Get the split position
    return Position                                 # Return the position

def parsePersonalDetails(PRawHtml: str) -> dict:
    """
    Parses the personal details of a player from the raw HTML of the player page.

    Args:
        PRawHtml (str): The raw HTML of the player page.

    Returns:
        dict: A dictionary containing the personal details of the player, currently only containing the date of birth.
    """
    Soup = BeautifulSoup(PRawHtml, "html.parser")                           # Parse the raw HTML
    DateOfBirth = Soup.find("div", id="pcm-player-dob").text.strip()    # Get the date of birth
    PersonalDetailsDict = {"DateOfBirth": DateOfBirth}                      # Create a dictionary with the date of birth (and possible future details)
    return PersonalDetailsDict                                              # Return the dictionary  

def parseSeasonAllGoalieStas(PRawHtml: str) -> dict:
    """
    Parses the total stats for a player from the raw HTML of the player page.

    Args:
        PRawHtml (str): The raw HTML of the player page.

    Returns:
        dict: A dictionary containing the total stats for the player. All values are STRINGS!.
        {
            "Games": Games (number of games played)
            "Played": Played (number of games played)
            "GoalsAllowed": GoalsAllowed (number of goals allowed)
            "TimeOnIce": TimeOnIce (number of minutes played)
            "Gaa": Gaa (number of goals against average)
        }
    """
    Soup = BeautifulSoup(PRawHtml, "html.parser")                                   # Parse the raw HTML. Values below are clean strings
    Games = Soup.find("div", id="pcas-goalie-games").text.strip()                   # How many game the goalie was in the roster for
    Played = Soup.find("div", id="pcas-goalie-played-games").text.strip()           # How many games the goalie played
    GoalsAllowed = Soup.find("div", id="pcas-goalie-goals-against").text.strip()    # How many goals the goalie allowed
    TimeOnIce = Soup.find("div", id="pcas-goalie-toi").text.strip()                 # How much time on ice the goalie had
    Gaa = Soup.find("div", id="pcas-goalie-gaa").text.strip()                       # What has the goalies GAA

    SeasonAllGoalieStasDict = {"Games": Games, "Played": Played, "GoalsAllowed": GoalsAllowed, "TimeOnIce": TimeOnIce, "Gaa": Gaa}
    return SeasonAllGoalieStasDict

def parseSeasonAllPlayerStas(PRawHtml: str) -> dict:
    """
    Parses the total stats for a skater from the raw HTML of the player page.

    Args:
        PRawHtml (str): The raw HTML of the player page.

    Returns:
        dict: A dictionary containing the total stats for the skater. All values are STRINGS!.
        {
            "Games": Games (number of games played),
            "Goals": Goals (number of goals scored),
            "Assists": Assists (number of assists),
            "Points": Points (total points),
            "PenaltyMinutes": PenaltyMinutes (number of penalty minutes),
            "PpGoals": PpGoals (number of power play goals),
            "ShGoals": ShGoals (number of short handed goals),
            "SoGoals": SoGoals (number of shootout goals)
        }
    """

    Soup = BeautifulSoup(PRawHtml, "html.parser")                                       # Parse the raw HTML. Values below are clean strings
    Games = Soup.find("div", id="pcas-skater-games").text.strip()                       # How many games the player played
    Goals = Soup.find("div", id="pcas-skater-goals").text.strip()                       # How many goals the player scored
    Assists = Soup.find("div", id="pcas-skater-assists").text.strip()                   # How many assists they had
    Points = Soup.find("div", id="pcas-skater-points").text.strip()                     # How many points they had
    PenaltyMinutes = Soup.find("div", id="pcas-skater-penalty-minutes").text.strip()    # How many penalty minutes they had
    PpGoals = Soup.find("div", id="pcas-skater-goals-pp").text.strip()                  # How many power play goals
    ShGoals = Soup.find("div", id="pcas-skater-goals-sh").text.strip()                  # How many short handed goals
    SoGoals = Soup.find("div", id="pcas-skater-goals-ws").text.strip()                  # How many shootout goals
    
    SeasonAllPlayerStasDict = {"Games": Games, "Goals": Goals, "Assists": Assists, "Points": Points, "PenaltyMinutes": PenaltyMinutes, "PpGoals": PpGoals, "ShGoals": ShGoals, "SoGoals": SoGoals}
    return SeasonAllPlayerStasDict

def parseGoalieStats(PRawHtml: str) -> dict:
    """
    Parses the goalie stats for each level from the raw HTML of the player's page.

    Args:
        PRawHtml (str): The raw HTML of the player's page.

    Returns:
        list[dict]: A list of dictionaries, each containing stats for a team at a specific level in a season.
        Each dictionary includes:
            - "TeamName": The name of the team.
            - "LevelName": The name of the level.
            - "Games": The number of games in the roster.
            - "Played": The number of games played.
            - "GoalsAllowed": The number of goals allowed.
            - "Saves": The number of saves made.
            - "Save%": The save percentage.
    """

    Soup = BeautifulSoup(PRawHtml, "html.parser")   # Parse the raw HTML
    Rows = Soup.find_all("div", class_="pcss-level-title-row")
    
    AllLevelsInSeason = []    # This holds all the dicts for inividual teams on a season

    for Row in Rows:
        LevelDict = {}        # Create a dictionary for each level
        Cells = Row.find_all("div", class_="pcss-level-stat-col")
        TeamName = Row.find("div", class_="pcss-level-team-name-col").text.strip()
        LevelName = Row.find("div", class_="pcss-level-name-col").text.strip()

        # print(f"Team: {TeamName} | Level: {LevelName} | Games: {Cells[0].text.strip()} | Played: {Cells[1].text.strip()} | GoalsAllowed: {Cells[2].text.strip()} | Saves: {Cells[3].text.strip()} | Save%: {Cells[4].text.strip()}")
        # print("")

        LevelDict["TeamName"] = TeamName                    # Add the team name
        LevelDict["LevelName"] = LevelName                  # Add the level name
        LevelDict["Games"] = Cells[0].text.strip()          # Add the number of games in the roster
        LevelDict["Played"] = Cells[1].text.strip()         # Add the number of played
        LevelDict["GoalsAllowed"] = Cells[2].text.strip()   # Add the number of goals allowed
        LevelDict["Saves"] = Cells[3].text.strip()          # Add the number of saves
        LevelDict["Save%"] = Cells[4].text.strip()          # Add the save percentage

        AllLevelsInSeason.append(LevelDict)

    return AllLevelsInSeason



def parsePlayerStats(PRawHtml: str) -> list[dict]:
    """
    Parses the player stats for a player from the raw HTML of the player page.

    Args:
        PRawHtml (str): The raw HTML of the player page.

    Returns:
        dict: A dictionary containing the player stats for the player, currently only containing the number of goals.
        {

        }
    """
    Soup = BeautifulSoup(PRawHtml, "html.parser")   # Parse the raw HTML
    Rows = Soup.find_all("div", class_="pcss-level-title-row")
    
    AllLevelsInSeason = []    # This holds all the dicts for inividual teams on a season

    for Row in Rows:
        LevelDict = {}
        Cells = Row.find_all("div", class_="pcss-level-stat-col")
        TeamName = Row.find("div", class_="pcss-level-team-name-col").text.strip()
        LevelName = Row.find("div", class_="pcss-level-name-col").text.strip()
        
        # print(f"Team: {TeamName} | Level: {LevelName} | Games: {Cells[0].text.strip()} | Goals: {Cells[1].text.strip()} | Assists: {Cells[2].text.strip()} | Points: {Cells[3].text.strip()} | PenaltyMinutes: {Cells[4].text.strip()}")
        # print("")
        
        LevelDict["TeamName"] = TeamName                    # Add the team name
        LevelDict["LevelName"] = LevelName                  # Add the level name
        LevelDict["Games"] = Cells[0].text.strip()          # Add the number of games in the roster
        LevelDict["Goals"] = Cells[1].text.strip()          # Add the number of goals
        LevelDict["Assists"] = Cells[2].text.strip()        # Add the number of assists
        LevelDict["Points"] = Cells[3].text.strip()         # Add the number of points
        LevelDict["PenaltyMinutes"] = Cells[4].text.strip() # Add the number of penalty minutes

        AllLevelsInSeason.append(LevelDict)

    return AllLevelsInSeason



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

def fetchRetiredPlayerCareerData(PPlayerLink: str, PPlayerObject: Player, PPage: object) -> dict:
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


        else: # If position is "Kenttäpelaaja"
            print(f"{Season} SeasonAllPlayerStas: {StatsDict["SeasonAllPlayerStas"]}")
            for Level in StatsDict["PlayerLevelStats"]:   # DEBUG PRINT
                print(f"{Level}")
            # PlayerDataDict[Season] = StatsDict
            SeasonObject = PlayerSeason(Season, StatsDict["SeasonAllPlayerStas"])


    return None

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
        print(f"Failed to scrape {PPlayerObject.sjlName}")                  # This is a player that is no more active, so sjl displays the information differently.
        fetchRetiredPlayerCareerData(PPlayerLink, PPlayerObject, PPage)     # This function does its best to handle the case, and still record all available data.
        return None                                                         # Terminate the regular scraping. 

    scrapeSeasonsForPlayer(PPlayerObject, PPage)                            # Scrape the player's seasons. Outcome Player.seasons <- SeasonObject.seasonLeveStats <- SeasonLevelObject


    return None

if __name__ == "__main__":
    pass