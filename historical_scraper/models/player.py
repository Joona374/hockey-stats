class Player:
    def __init__(self, sjlName, epName, sjlLink):
        self.sjlName = sjlName
        self.epName = epName
        self.sjlLink = sjlLink
        self.birthYear = None
        self.position = None
        self.seasons = []

    def __str__(self):
        return f"{self.sjlName} {self.position}"

    def addSeason(self, season):
        self.seasons.append(season)
        return None