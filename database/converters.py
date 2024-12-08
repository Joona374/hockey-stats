from database.models import Player as PlayerRow, GoalieSeason as GoalieSeasonRow, PlayerSeason as PlayerSeasonRow, PlayerSeasonLevel as PlayerSeasonLevelRow, GoalieSeasonLevel as GoalieSeasonLevelRow, Club as ClubRow, Level as LevelRow, AgeGroup as AgeGroupRow

from historical_scraper.models.player import Player as PlayerObject
from historical_scraper.models.season import GoalieSeason as GoalieSeasonObject, PlayerSeason as PlayerSeasonObject, PlayerSeasonLevel as PlayerSeasonLevelObject, GoalieSeasonLevel as GoalieSeasonLevelObject 

def playerConverter(PlayerObject: PlayerObject) -> PlayerRow:
    """
    Converts a PlayerObject to a PlayerRow (Base).
    
    Args:
        PlayerObject (Player): The PlayerObject to convert. This is the Object from scraping the player's page.
    
    Returns:
        PlayerRow: The converted PlayerRow (Base). This is the row in the "players" table in the database.
    """
    return PlayerRow(
        sjlName = PlayerObject.sjlName,
        epName = PlayerObject.epName,
        sjlLink = PlayerObject.sjlLink,
        position = PlayerObject.position,
        birthYear = PlayerObject.birthYear
    )

def goalieSeasonConverter(GoalieSeasonObject: GoalieSeasonObject, PplayerId: int) -> GoalieSeasonRow:
    """
    Converts a GoalieSeasonObject to a GoalieSeasonRow (Base).
    
    Args:
        GoalieSeasonObject (GoalieSeason): The GoalieSeasonObject to convert. This is the Object from scraping the goalie's page.
        PplayerId (int): The id of the player row in the players table.
    
    Returns:
        GoalieSeasonRow: The converted GoalieSeasonRow (Base). This is the row in the "goalies" table in the database.
    """    
    SplitTOI = GoalieSeasonObject.timeOnIce.split(":")
    Seconds = int(SplitTOI[0]) * 60 + int(SplitTOI[1])
    ParsedTimeOnIce = Seconds / 60
    
    return GoalieSeasonRow(
        year = GoalieSeasonObject.year,
        games = GoalieSeasonObject.games,
        played = GoalieSeasonObject.played,
        goalsAllowed = GoalieSeasonObject.goalsAllowed,
        timeOnIce = ParsedTimeOnIce,
        gaa = GoalieSeasonObject.gaa,
        playerId = PplayerId        # This is not available in the GoalieSeasonObject, as the id is the "row id" in the players table in the database.
    )

def playerSeasonConverter(PlayerSeasonObject: PlayerSeasonObject, PplayerId: int) -> PlayerSeasonRow:
    """
    Converts a PlayerSeasonObject to a PlayerSeasonRow (Base).
    
    Args:
        PlayerSeasonObject (PlayerSeason): The PlayerSeasonObject to convert. This is the Object from scraping the player's page.
        PplayerId (int): The id of the player row in the players table.
    
    Returns:
        PlayerSeasonRow: The converted PlayerSeasonRow (Base). This is the row in the "player_seasons" table in the database.
    """
    return PlayerSeasonRow(
        year = PlayerSeasonObject.year,
        games = PlayerSeasonObject.games,
        goals = PlayerSeasonObject.goals,
        assists = PlayerSeasonObject.assists,
        points = PlayerSeasonObject.points,
        penaltyMinutes = PlayerSeasonObject.penaltyMinutes,
        ppGoals = PlayerSeasonObject.ppGoals,
        shGoals = PlayerSeasonObject.shGoals,
        soGoals = PlayerSeasonObject.soGoals,
        playerId = PplayerId        # This is not available in the PlayerSeasonObject, as the id is the "row id" in the players table in the database.
    )

def goalieSeasonLevelConverter(GoalieSeasonLevelObject: GoalieSeasonLevelObject, 
                               seasonRowId: int,
                               clubRowId: int, 
                               levelRowId: int, 
                               ageGroupRowId: int,
                               playerId: int
                               ) -> GoalieSeasonLevelRow:
    """
    Converts a GoalieSeasonLevelObject to a GoalieSeasonLevelRow (Base).
    
    Args:
        GoalieSeasonLevelObject (GoalieSeasonLevel): The GoalieSeasonLevelObject to convert. This is the Object from scraping the goalie's page.
        seasonRowId (int): The id of the goalie season row in the goalie_seasons table.
        clubRowId (int): The id of the club row in the clubs table.
        levelRowId (int): The id of the level row in the levels table.
        ageGroupRowId (int): The id of the age group row in the age_groups table.
        playerId (int): The id of the player row in the players table.
    
    Returns:
        GoalieSeasonLevelRow: The converted GoalieSeasonLevelRow (Base). This is the row in the "goalie_season_levels" table in the database.
    """
    
    return GoalieSeasonLevelRow(
        # These are all ids pointing to rows in different tables. They are passed as parameters.
        clubId = clubRowId,         # Points to the row in "clubs" table - clubs.id
        levelId = levelRowId,       # Points to the row in "levels" table - levels.id
        ageGroupId = ageGroupRowId, # Points to the row in "age_groups" table - age_groups.id
        seasonId = seasonRowId,     # Points to the row in "goalie_seasons" table - goalie_seasons.id
        playerId = playerId,        # Points to the row in "players" table - players.id

        # These are the values from the GoalieSeasonLevelObject
        games = GoalieSeasonLevelObject.games,
        played = GoalieSeasonLevelObject.played,
        goalsAllowed = GoalieSeasonLevelObject.goalsAllowed,
        saves = GoalieSeasonLevelObject.saves,
        savePercentage = GoalieSeasonLevelObject.savePercentage
    )

def playerSeasonLevelConverter(PlayerSeasonLevelObject: PlayerSeasonLevelObject, 
                               seasonRowId: int,
                               clubRowId: int,
                               levelRowId: int,
                               ageGroupRowId: int,
                               playerId: int
                               ) -> PlayerSeasonLevelRow:
    """
    Converts a PlayerSeasonLevelObject to a PlayerSeasonLevelRow (Base).
    
    Args:
        PlayerSeasonLevelObject (PlayerSeasonLevel): The PlayerSeasonLevelObject to convert. This is the Object from scraping the player's page.
        seasonRowId (int): The id of the player season row in the player_seasons table.
        clubRowId (int): The id of the club row in the clubs table.
        levelRowId (int): The id of the level row in the levels table.
        ageGroupRowId (int): The id of the age group row in the age_groups table.
        playerId (int): The id of the player row in the players table.
    
    Returns:
        PlayerSeasonLevelRow: The converted PlayerSeasonLevelRow (Base). This is the row in the "player_season_levels" table in the database.
    """
    
    return PlayerSeasonLevelRow(
        # These are all ids pointing to rows in different tables. They are passed as parameters.
        clubId = clubRowId,         # Points to the row in "clubs" table - clubs.id
        levelId = levelRowId,       # Points to the row in "levels" table - levels.id
        ageGroupId = ageGroupRowId, # Points to the row in "age_groups" table - age_groups.id
        seasonId = seasonRowId,     # Points to the row in "player_seasons" table - player_seasons.id
        playerId = playerId,        # Points to the row in "players" table - players.id

        # These are the values from the PlayerSeasonLevelObject
        games = PlayerSeasonLevelObject.games,
        goals = PlayerSeasonLevelObject.goals,
        assists = PlayerSeasonLevelObject.assists,
        points = PlayerSeasonLevelObject.points,
        penaltyMinutes = PlayerSeasonLevelObject.penaltyMinutes
    )

def createClubRow(clubNameInput: str) -> ClubRow:
    """
    Creates a new ClubRow with the given clubNameInput. The clubName is the name of the club.
    
    Args:
        clubNameInput (str): The name of the club.
    
    Returns:
        ClubRow: The created ClubRow (Base)
    """
    return ClubRow(clubName = clubNameInput)

def createLevelRow(levelNameInput: str) -> LevelRow:
    """
    Creates a new LevelRow with the given levelNameInput. The levelName is the name of the level.
    
    Args:
        levelNameInput (str): The name of the level.
    
    Returns:
        LevelRow: The created LevelRow (Base)
    """
    return LevelRow(levelName = levelNameInput)

def createAgeGroupRow(ageGroupNameInput: str) -> AgeGroupRow:
    """
    Creates a new AgeGroupRow with the given ageGroupNameInput. The ageGroupName is the name of the age group.
    
    Args:
        ageGroupNameInput (str): The name of the age group.
    
    Returns:
        AgeGroupRow: The created AgeGroupRow (Base)
    """

    return AgeGroupRow(ageGroupName = ageGroupNameInput)
