import sys
from pathlib import Path
# Add the root directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

from scraper_helpers.scrape_team_data_helpers import fetchTeamHtml, parsePlayerRowsFromHtml
from scraper_helpers.scrape_player_data_helpers import *
from config import CURRENT_YEAR
from scraper_helpers.classes import *

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

    else:
        AgeGroup, Level = PLevelSeason.levelName.split(" ")
        Club = PLevelSeason.teamName.split(" ")[0].rstrip(",")

    PLevelSeason.ageGroup = AgeGroup
    PLevelSeason.level = Level
    PLevelSeason.club = Club

    return None

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

def scrapeTeamData(PTeamId: int, PPage: object, PClubList: list, PSeasons: list[str]) -> list[dict]:
        print("Starting to scrape team: " + PTeamId)

        # Go to the teams page
        Link = f"https://www.leijonat.fi/index.php/index.php/joukkueet?teamid={PTeamId}"
        PPage.goto(Link)
        PPage.wait_for_timeout(000)  
        PPage.wait_for_selector("#tcm-team-official-name", timeout=5000)

        TeamName = PPage.locator("#tcm-team-official-name").inner_html() # Scrape the name of team
        TeamObject = Team(TeamName, PTeamId, Link)                       # Create the TeamObject for each TeamId and init it with the TeamName, TeamId and the SjlLink
        fetchTeamHtml(PSeasons, PPage, TeamObject)                        # This writes the HTML for each requested season in the "Seasons" dict: "Seasons": {"2025": HTML, "2024": HTML, "2023": HTML...}
        PClubList.append(TeamObject)

def scrapeClubData(PTeamIds: list[str], PNumberOfSeasons: int, PClubList: list, Page: object) -> None:
    """
    Scrapes the player data for a list of teams.

    Args:
        PTeamIds (list[str]): The team IDs of the teams to scrape.
        PNumberOfSeasons (int): The number of seasons to scrape.
        PClubList (list[object]): A list to hold the team objects that store the data.

    Returns:
        None: Edits in place the PClubDict dictionary, each containing the scraped historical data for a team. This dicts contain:
            - "TeamName": The name of the team.
                - "SjlLink": The link to the team's SJL page.
                - "TeamId": The ID of the team.
                - "Seasons": A dictionary of seasons and their HTML.
                    - "Season": The html of the players of the season.
    """
    Seasons = []                                # Local container for the years to scrape 
    getSeasons(PNumberOfSeasons, Seasons)       # Populates the list with year strings ["2025", "2024"...]
    
    # SCRAPE THE EACH TEAM GIVEN IN THE PTeamIds.
    # SCRAPE THE HTML CONTAINING THE PLAYERS (parsed later) FOR EACH TEAM
    for TeamId in PTeamIds:
        scrapeTeamData(TeamId, Page, PClubList, Seasons)
        
    # Cleanup
    Seasons.clear()
    print("Done scraping the teams player htmls.")



def main():
    print("Scraping script is live")
    
    # Init the containers
    ClubTeamList = []   # List of Team objects. These mainly just contain the html of the players for each season. Used just until we manage to parse the html into objects.
    PlayersDict = {}     # Dict of player objects. These contain all the player objects containing the actual data
    
    with sync_playwright() as p:
        # Init the browser
        Browser = p.chromium.launch(headless=True)
        Page = Browser.new_page()   # USE THIS PAGE EVERYWHERE!

        # This scrapes the team pages for the html that contain all players for a specific season.
        # Args: PTeamIds: List of teamIds, PNumberOfSeasons: Number of seasons to scrape (going back from current), PClubList: List to contain Team objects
        scrapeClubData(["319126555"], 1, ClubTeamList, Page)                ### !!Eventually the club IDs should be more dynamic!! ###

        # This parses the html from each teams each season into player objects. The player objects get stored in PlayersDict with no duplicates.
        for Team in ClubTeamList:
            for SeasonKey, HtmlValue in Team.seasonRosterHtmls.items():     # Key is the season year (ex. "2025"), value is the html (containing all the players for that season)
                parsePlayerRowsFromHtml(HtmlValue, PlayersDict)             # Parses the players from html to player objects. These objects only contain the sjl_name, ep_name, and sjl_link at this point.
        print("Done parsing the players")

        for NameKey, ValueObject in PlayersDict.items():                    # Here value is a Player object
            fetchPlayerCareerData(ValueObject.sjlLink, ValueObject, Page)   # This edits the value Player object in place

        # Cleanup
        Browser.close()

    # This writes the .level .club and .ageGroup attributes to the PlayerSeasonLevel objects
    writeSeasonLevelDetails(PlayersDict)
    
    ClubTeamList.clear()
    PlayersDict.clear()

    return None
    
def writeSeasonLevelDetails(PPlayersDict: dict):
    for NameKey, Player in PPlayersDict.items():
        for season in Player.seasons:
            for LevelStats in season.seasonLevelStats:
                parseAgeGroupLevelAndClub(LevelStats)
                print(LevelStats)


if __name__ == "__main__":
    main()
    # Players = scrapeTeamData("319126555")     # Test teamId = "319126555"
    # scrapePlayerData("https://www.leijonat.fi/index.php/index.php/pelaajat?lkq=570077486031233381583197&zwf=dc5f8f2fbc1e7307c13380dcbbefa68b", EmptyDict) # GOALIE
    # scrapePlayerData("https://www.leijonat.fi/index.php/index.php/pelaajat?lkq=712154746086211468606295&zwf=5a69f51b7ddadf6b07e4bf624109f894", EmptyDict) # SKATER

