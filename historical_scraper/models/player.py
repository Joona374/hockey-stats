class Player:
    """
    A Player object stores data about a single player. The attributes are:

    - sjlName (str): The player's name in the format "LASTNAME Firstname".
    - epName (str): The player's name in the format "Firstname Lastname".
    - sjlLink (str): A link to the player's page on the SJL website.
    - birthYear (int): The player's birth year.
    - position (str): The player's position, either "Maalivahti" or "Kenttäpelaaja", "Hyökkääjä" or "Puolustaja".
    - seasons (list): A list of the player's seasons, which are objects of class GoalieSeason or PlayerSeason.
    """

    def __init__(self, sjlName, epName, sjlLink):
        """Initializes a Player object."""
        self.sjlName = sjlName
        self.epName = epName
        self.sjlLink = sjlLink
        self.birthYear = None
        self.position = None
        self.seasons = []

    def __str__(self):
        """Returns a string representation of the Player object."""
        return f"{self.sjlName} {self.position} {self.seasons} Player Object str representation"

    def addSeason(self, season):
        """Adds a season object to the player's list of seasons."""
        self.seasons.append(season)
        return None
