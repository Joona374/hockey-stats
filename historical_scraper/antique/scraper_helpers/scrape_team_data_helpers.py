from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from scraper_helpers.classes import Team, Player


def fetchTeamHtml(PSeasons: list[str], PPage: object, PTeamObject: Team) -> None:
    """
    Fetches the HTML for all the players for a given season.

    Args:
        PSeasons (list[str]): The seasons to fetch.
        PPage (object): The page object from playwright.
        PTeamObject (Team): The team object from scraper.scrapeClubData().

    Returns:
        None: Edits in place the PTeamObject. Updates the self.seasonRosterHtmls dict. Adds each season "year": "html".
    """
    for Season in PSeasons: # PSeasons is a lsit of years like ["2025", "2024"...]
        print("Scraping season: " + Season + " for team: " + PTeamObject.name)
        PPage.locator("select#tcss-season-select").select_option(Season)    # This sets the season selector to current season to load dynamic html for season.
        # Wait a bit to load dynamic content. Should this be adjusted?
        PPage.wait_for_timeout(1000)  

        # Get the content of the players container on the team page (PELAAJAT)
        RawHtml = PPage.locator("#tcst-team-players-container").inner_html()

        # We use the Team objects method to store the season: html key-value pair to the dict.
        PTeamObject.addSeasonRosterHtml(Season, RawHtml)    # Add the html to the dict

    return None


def parsePlayerRowsFromHtml(PRawHtml: str, PPlayersDict: dict, PParseStaff: bool = False) -> list[dict]:
    """
    Parses the player (and staff) rows from the raw HTML of a teams one seasons player container.

    Args:
        PRawHtml (str): The raw HTML of the players container. This HTML contains all players for a season.
        PParseStaff (bool): Whether to parse staff members.

    Returns:
        list[dict]: A list (and staff) of player dictionaries, containing the name in SJL format, the name in EP format, and the link to the player's page:
        \n      {
        \n      PlayerDict["SjlName"] = SjlName
        \n      PlayerDict["EpName"] = EpName
        \n      PlayerDict["SjlLink"] = f"https://www.leijonat.fi/index.php/index.php/{NameLink["href"]}"
        \n      }
    """

    # Make a list of all the player rows
    Soup = BeautifulSoup(PRawHtml, "html.parser")
    Rows = Soup.find_all("div", class_="tcst-row")

    for Row in Rows:        # Loop through the player rows, meaning handle each players html at time
        RoleDiv = Row.find("div", class_="col-xs-4")    # Find the role div
        if RoleDiv:
            Role = RoleDiv.text.strip()                  # Get the role
            if Role == "Toimihenkilö" and PParseStaff == False:
                continue    # Skip staff members
        else:
            print("No role div") # Role div not found SOS? :D


        NameDiv = Row.find("div", class_="col-xs-6")    # Find the div containing both the name and player-page link

        if NameDiv:
            PlayerLink = NameDiv.find("a")                # Find the link to the players page
            if PlayerLink:
                SjlName = PlayerLink.text.strip()       # Get the name in SJL format
                NameParts = SjlName.split(" ")        # Split the name into first name and last name
                EpName = f"{NameParts[1]} {NameParts[0].capitalize()}"  # Get the name in EP format

                # Create a player object, and save the names and link to the player object
                PlayerObject = Player(SjlName, EpName, f"https://www.leijonat.fi/index.php/index.php/{PlayerLink['href']}")     # Create a player object

            else:
                print("No player link")
        else:
            print("No name div")
        
        if SjlName not in PPlayersDict: # Check if the player (object) is already in the dict. This is to avoid duplicates.
            PPlayersDict[SjlName] = PlayerObject # This edits the dict in place. Each player is a Player object.
        else:
            print(f"Player {SjlName} already in dict")

    return None

if __name__ == "__main__":
    pass