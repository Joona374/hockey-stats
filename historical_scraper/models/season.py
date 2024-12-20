class GoalieSeason:
    """
    This class stores a single year combined season stats and season level stat objects for a goalie
    statsDict is a dictionary with the following keys: Games, Played, GoalsAllowed, TimeOnIce, Gaa
    The atributes that are used when converting to a Row:
        - year
        - games
        - played
        - goalsAllowed
        - timeOnIce
        - gaa
        - seasonLevelStats (list of GoalieSeasonLevel objects). This is just a relationship to the GoalieSeasonsLevels table.
    """
    def __init__(self, year, statsDict):
        self.year = year
        self.statsDict = statsDict
        self.seasonLevelStats = []
        self.createStats()

    def createStats(self):
        """
        Parses the statsDict and assigns the values to the instance variables:
        - games: Number of games in the roster.
        - played: Number of games played.
        - goalsAllowed: Number of goals allowed.
        - timeOnIce: Total time on ice.
        - gaa: Goals against average.
        """

        self.games = self.statsDict['Games']
        self.played = self.statsDict['Played']
        self.goalsAllowed = self.statsDict['GoalsAllowed']
        self.timeOnIce = self.statsDict['TimeOnIce']
        self.gaa = self.statsDict['Gaa']

    def addLevelStat(self, levelStat):
        """
        Adds a GoalieSeasonLevel object to the list of season level stats.

        Args:
            levelStat (GoalieSeasonLevel): The level stat object to be added to the seasonLevelStats list.
        """

        self.seasonLevelStats.append(levelStat)

    def __str__(self):
        return f"{self.year} Played: {self.played} GAA: {self.gaa}"

class PlayerSeason:
    """
    This class stores a single year combined season stats and season level stat objects for a skater
    statsDict is a dictionary with the following keys: Games, Goals, Assists, Points, PenaltyMinutes, PpGoals, ShGoals, SoGoals
    The atributes that are used when converting to a Row:
        - year
        - games
        - goals
        - assists
        - points
        - penaltyMinutes
        - ppGoals
        - shGoals
        - soGoals
        - seasonLevelStats (list of PlayerSeasonLevel objects). This is just a relationship to the PlayerSeasonsLevels table.
    """
    def __init__(self, year, statsDict):
        self.year = year
        self.statsDict = statsDict
        self.seasonLevelStats = []
        self.createStats()

    def createStats(self):
        """
        Parses the statsDict and assigns the values to the instance variables:
        - games: Number of games in the roster.
        - goals: Number of goals scored.
        - assists: Number of assists.
        - points: Total points.
        - penaltyMinutes: Number of penalty minutes.
        - ppGoals: Number of power play goals.
        - shGoals: Number of short handed goals.
        - soGoals: Number of shootout goals.
        """
        self.games = self.statsDict['Games']
        self.goals = self.statsDict['Goals']
        self.assists = self.statsDict['Assists']
        self.points = self.statsDict['Points']
        self.penaltyMinutes = self.statsDict['PenaltyMinutes']
        self.ppGoals = self.statsDict['PpGoals']
        self.shGoals = self.statsDict['ShGoals']
        self.soGoals = self.statsDict['SoGoals']

    def addLevelStat(self, levelStat):
        """
        Adds a PlayerSeasonLevel object to the list of season level stats  
        """
        self.seasonLevelStats.append(levelStat)

    def __str__(self):
        return f"{self.year} Played: {self.games} Points: {self.points}"



class GoalieSeasonLevel:
    """
    Creates a GoalieSeasonLevel object from a given dictionary of stats. The dictionary should contain the following keys:
    - TeamName
    - LevelName
    - Games
    - Played
    - GoalsAllowed
    - Saves
    - Save%\n
    The createStats method is called to parse the dictionary and assign to instance variables. The club, level, and ageGroup instance variables are also set to None. 
    These are parsed at a later state in helpers.player_scraper.writeSeasonLevelDetails
    """
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
        return f"Team: {self.club} | AgeGroup: {self.ageGroup} | Level: {self.level} | Played: {self.played} | Save%: {self.savePercentage}%"

class PlayerSeasonLevel:
    """
    Creates a PlayerSeasonLevel object from a given dictionary of stats. The dictionary should contain the following keys:
    - TeamName
    - LevelName
    - Games
    - Goals
    - Assists
    - Points
    - PenaltyMinutes
    The createStats method is called to parse the dictionary and assign to instance variables. The club, level, and ageGroup instance variables are also set to None. 
    These are parsed at a later state in helpers.player_scraper.writeSeasonLevelDetails
    """
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