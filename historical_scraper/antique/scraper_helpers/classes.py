# This class is used to just collect and hold all the data. 
# seasonRosterHtmls will store the roster htmls before we start the parsing. It is a dict where the key is the year and the value is a string of html.
class Team:
    def __init__(self, name, teamId, sjlLink):
        self.name = name
        self.teamId = teamId
        self.sjlLink = sjlLink
        self.seasonRosterHtmls = {}

    def addSeasonRosterHtml(self, season, seasonRosterHtml):
        self.seasonRosterHtmls[season] = seasonRosterHtml

    

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

class Season:
    def __init__(self, year):
        self.year = year
        self.levelStats = []
    
    def addLevelStat(self, levelStat):
        self.levelStats.append(levelStat)

class GoalieSeason:
    def __init__(self, year, statsDict):
        self.year = year
        self.statsDict = statsDict
        self.seasonLevelStats = []
        self.createStats()

    def createStats(self):
        self.games = self.statsDict['Games']
        self.played = self.statsDict['Played']
        self.goalsAllowed = self.statsDict['GoalsAllowed']
        self.timeOnIce = self.statsDict['TimeOnIce']
        self.gaa = self.statsDict['Gaa']
        self.seasonLevelStats = []

    def __str__(self):
        return f"{self.year} Played: {self.played} GAA: {self.gaa}"
        

    def addLevelStat(self, levelStat):
        self.seasonLevelStats.append(levelStat)



class PlayerSeason:
    def __init__(self, year, statsDict):
        self.year = year
        self.statsDict = statsDict
        self.seasonLevelStats = []
        self.createStats()

    def addLevelStat(self, levelStat):
        self.seasonLevelStats.append(levelStat)

    def __str__(self):
        return f"{self.year} Played: {self.games} Points: {self.points}"

    def createStats(self):
        self.games = self.statsDict['Games']
        self.goals = self.statsDict['Goals']
        self.assists = self.statsDict['Assists']
        self.points = self.statsDict['Points']
        self.penaltyMinutes = self.statsDict['PenaltyMinutes']
        self.ppGoals = self.statsDict['PpGoals']
        self.shGoals = self.statsDict['ShGoals']
        self.soGoals = self.statsDict['SoGoals']
        self.seasonLevelStats = []

class GoalieSeasonLevel:
    def __init__(self, statsDict):
        self.statsDict = statsDict
        self.createStats()
        self.club = None
        self.level = None
        self.ageGroup = None      

    def createStats(self):
        self.teamName = self.statsDict["TeamName"]
        self.levelName = self.statsDict["LevelName"]
        self.games = self.statsDict["Games"]
        self.played = self.statsDict["Played"]
        self.goalsAllowed = self.statsDict["GoalsAllowed"]
        self.saves = self.statsDict["Saves"]
        self.savePercentage = self.statsDict["Save%"]

    def __str__(self):
        return f"Team: {self.club} | AgeGroup: {self.ageGroup} | Level: {self.level} | Played: {self.played} | Points: {self.savePercentage}"

class PlayerSeasonLevel:
    def __init__(self, levelDict):
        self.levelDict = levelDict
        self.createStats()
        self.club = None
        self.level = None
        self.ageGroup = None

    def createStats(self):
        self.teamName = self.levelDict['TeamName']
        self.levelName = self.levelDict['LevelName']
        self.games = self.levelDict['Games']
        self.goals = self.levelDict['Goals']
        self.assists = self.levelDict['Assists']
        self.points = self.levelDict['Points']
        self.penaltyMinutes = self.levelDict['PenaltyMinutes']

    def __str__(self):
        return f"Team: {self.club} | AgeGroup: {self.ageGroup} | Level: {self.level} | Games: {self.games} | Points: {self.points}"


if __name__ == "__main__":
    print("Go run the scraper.py dumb dumb :D")