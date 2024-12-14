from playwright.sync_api import sync_playwright

from historical_scraper.helpers.team_scraper import scrapeClubData, parsePlayerRowsFromHtml
from historical_scraper.helpers.player_scraper import fetchPlayerCareerData, writeSeasonLevelDetails
from historical_scraper.models.team import Team
from historical_scraper.models.player import Player
from historical_scraper.config import CURRENT_YEAR

from database.reader import getDbContents

def oneGoalieTest():
    print("One goalie test script is live")
    
    # Init the containers
    ClubTeamList = []   # List of Team objects. These mainly just contain the html of the players for each season. Used just until we manage to parse the html into objects.
    PlayersDict = {}     # Dict of player objects. These contain all the player objects containing the actual data
    
    with sync_playwright() as p:
        # Init the browser
        Browser = p.chromium.launch(headless=True)
        Page = Browser.new_page()   # USE THIS PAGE EVERYWHERE WITHIN HISTORICAL SCRAPER!

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

def onePlayerTest():
    print("One Player test script is live")
    
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
                if "LAAKOLI Niilo" in PlayersDict:
                    break
        print("Done parsing the players")

        for NameKey, ValueObject in PlayersDict.items():                    # Here value is a Player object
            fetchPlayerCareerData(ValueObject.sjlLink, ValueObject, Page)   # This edits the value Player object in place
            if "LAAKOLI Niilo" in NameKey:
                break

        # Cleanup
        Browser.close()

    # This writes the .level .club and .ageGroup attributes to the PlayerSeasonLevel objects
    writeSeasonLevelDetails(PlayersDict)
    
    for player, object in PlayersDict.items():
        print(f"{player}: {object}")
    print("\n\n")
    print(PlayersDict["LAAKOLI Niilo"])
    OnePlayer = PlayersDict["LAAKOLI Niilo"]
    print(f"Second {OnePlayer}")

    # return OnePlayer
    return PlayersDict

def main():
    print("Scraping script is live")
    
    # Init the containers
    ClubTeamList = []           # List of Team objects. These mainly just contain the html of the players for each season. Used just until we manage to parse the html into objects.
    PlayersDict = {}            # Dict of player objects. These contain all the player objects containing the actual data
    
    dbDict = getDbContents()    # To avoid dublicates, queries the database and returns all contents of "players", "clubs", "levels" and "age_groups" tables.
                                # This is a dict with keys "players", "clubs", "levels" and "age_groups".
                                # The values are also keys. For "players" the dict is {"sjlName": Player object (Base)}
    with sync_playwright() as p:
        # Init the browser
        Browser = p.chromium.launch(headless=True)
        Page = Browser.new_page()   # USE THIS PAGE EVERYWHERE!

        # This scrapes the team pages for the html that contain all players for a specific season.
        # Args: PTeamIds: List of teamIds, PNumberOfSeasons: Number of seasons to scrape (going back from current), PClubList: List to contain Team objects
        scrapeClubData(["319126555"], 2, ClubTeamList, Page)                ### !!Eventually the club IDs should be more dynamic!! ###

        # This parses the html from each teams each season into player objects. The player objects get stored in PlayersDict with no duplicates.
        for Team in ClubTeamList:
            for SeasonKey, HtmlValue in Team.seasonRosterHtmls.items():     # Key is the season year (ex. "2025"), value is the html (containing all the players for that season)
                parsePlayerRowsFromHtml(HtmlValue, PlayersDict)             # Parses the players from html to player objects. These objects only contain the sjl_name, ep_name, and sjl_link at this point.
        print("Done parsing the players")

        NameKeysToDelete = []                                               # List to collect the dict key-value pairs to delete
        for NameKey, ValueObject in PlayersDict.items():                    # Here key is sjlName format, ex. "DOE John", value is a Player object.
            if NameKey in dbDict["players"]:                                # Check if the player already exists in the db. If so, we dont scrape the player data
                print(f"{NameKey} is already in the database")              
                NameKeysToDelete.append(NameKey)                            # Add the key-value pair to the list of players to delete. These are already in the table, and we dont want to write duplicates.
                continue                                                    # Move to next player
            fetchPlayerCareerData(ValueObject.sjlLink, ValueObject, Page)   # This scrapes the players web page and edits the value Player object in place

        for NameKey in NameKeysToDelete:                                    # Delete the found duplicate players from the PlayersDict
            del PlayersDict[NameKey]                                        # This dict is later used to conver PlayerObjects to PlayerRows

        # Cleanup
        Browser.close()

    # This writes the .level .club and .ageGroup attributes to the PlayerSeasonLevel objects
    writeSeasonLevelDetails(PlayersDict)
    
    ClubTeamList.clear()
    

    return PlayersDict

if __name__ == "__main__":
    # main()
    oneGoalieTest()
