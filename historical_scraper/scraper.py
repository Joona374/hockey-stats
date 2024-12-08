# scraper.py

from playwright.sync_api import sync_playwright
from historical_scraper.helpers.team_scraper import scrapeClubData, parsePlayerRowsFromHtml
from historical_scraper.helpers.player_scraper import fetchPlayerCareerData, writeSeasonLevelDetails
from historical_scraper.models.team import Team
from historical_scraper.models.player import Player
from historical_scraper.config import CURRENT_YEAR

def oneGoalieTest():
    print("One goalie test script is live")
    
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
                parsePlayerRowsFromHtml(HtmlValue, PlayersDict)             # Parses the players from html to player objects. Key is sjlName format, ex. "DOE John" These objects only contain the sjl_name, ep_name, and sjl_link at this point.
                break
        print("Done parsing the players")

        for NameKey, ValueObject in PlayersDict.items():                    # Here value is a Player object
            fetchPlayerCareerData(ValueObject.sjlLink, ValueObject, Page)   # This edits the value Player object in place
            break

        # Cleanup
        Browser.close()

    # This writes the .level .club and .ageGroup attributes to the PlayerSeasonLevel objects
    writeSeasonLevelDetails(PlayersDict)
    
    for player, object in PlayersDict.items():
        print(f"{player}: {object}")
    print("\n\n")
    print(PlayersDict["PUUPPO Justus"])
    OneGoalie = PlayersDict["PUUPPO Justus"]
    print(f"Second {OneGoalie}")

    return OneGoalie

def main():
    print("Scraping script is live")
    
    # Init the containers
    ClubTeamList = []    # List of Team objects. These mainly just contain the html of the players for each season. Used just until we manage to parse the html into objects.
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
    

    return PlayersDict

if __name__ == "__main__":
    # main()
    oneGoalieTest()
