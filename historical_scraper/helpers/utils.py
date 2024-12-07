from config import CURRENT_YEAR
from bs4 import BeautifulSoup
from models import Player, GoalieSeason, PlayerSeason, GoalieSeasonLevel, PlayerSeasonLevel
import sys

def getSeasons(PAmmount: int, PSeasons: list[str]) -> None:
    """
    Appends the specified number of seasons to the provided list, starting from the current year (set in the config_file).

    Args:
        PAmmount (int): The number of seasons to append.
        PSeasons (list[str]): The list to which the seasons will be appended.

    Returns:
        None
    """

    for i in range(PAmmount):
        PSeasons.append(str(CURRENT_YEAR - i))
    return None

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

def parseAgeGroupLevelAndClub(PLevelSeason: object) -> None:
    """
    Parses the age group, level, and club from the PLevelSeason object and stores them back into the same object.
    These attributes are designed to be more usable when writing to a SQL database.

    Parameters:
        PLevelSeason (object): The object containing the data to be parsed.

    Returns:
        None
    """
    
    if PLevelSeason.levelName == "Harjoitusottelut":
        AgeGroup = None
        Level = "Harjoitusottelut"
        Club = PLevelSeason.teamName.split(" ")[0].rstrip(",")
        
    elif PLevelSeason.levelName == "Pohjola-leiri":
        AgeGroup = "U16"
        Level = "Pohjola-leiri"
        Club = None

    elif PLevelSeason.levelName == "Kartoitustapahtumat":
        AgeGroup = None
        Level = "Kartoitustapahtumat"
        Club = PLevelSeason.teamName

    elif "maaottelut" in PLevelSeason.levelName:
        AgeGroup = None
        Level = PLevelSeason.levelName
        Club = PLevelSeason.teamName

    else:
        AgeGroup, Level = PLevelSeason.levelName.split(" ")
        Club = PLevelSeason.teamName.split(" ")[0].rstrip(",")

    PLevelSeason.ageGroup = AgeGroup
    PLevelSeason.level = Level
    PLevelSeason.club = Club

    return None

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

