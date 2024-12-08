from database.models import Player as PlayerRow, GoalieSeason as GoalieSeasonRow, PlayerSeason as PlayerSeasonRow, PlayerSeasonLevel as PlayerSeasonLevelRow, GoalieSeasonLevel as GoalieSeasonLevelRow, Club as ClubRow, Level as LevelRow, AgeGroup as AgeGroupRow

from historical_scraper.models.player import Player as PlayerObject
from historical_scraper.models.season import GoalieSeason as GoalieSeasonObject, PlayerSeason as PlayerSeasonObject, PlayerSeasonLevel as PlayerSeasonLevelObject, GoalieSeasonLevel as GoalieSeasonLevelObject 

def playerConverter(PlayerObject: PlayerObject) -> PlayerRow:
    return PlayerRow(
        sjlName = PlayerObject.sjlName,
        epName = PlayerObject.epName,
        sjlLink = PlayerObject.sjlLink,
        position = PlayerObject.position,
        birthYear = PlayerObject.birthYear
    )

def goalieSeasonConverter(GoalieSeasonObject: GoalieSeasonObject, playerId: int) -> GoalieSeasonRow:
    return GoalieSeasonRow(
        year = GoalieSeasonObject.year,
        games = GoalieSeasonObject.games,
        played = GoalieSeasonObject.played,
        goalsAllowed = GoalieSeasonObject.goalsAllowed,
        timeOnIce = GoalieSeasonObject.timeOnIce,
        gaa = GoalieSeasonObject.gaa,
        player_id = playerId        # This is not available in the GoalieSeasonObject, as the id is the "row id" in the players table in the database.
    )

def playerSeasonConverter(PlayerSeasonObject: PlayerSeasonObject, playerId: int) -> PlayerSeasonRow:
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
        player_id = playerId        # This is not available in the PlayerSeasonObject, as the id is the "row id" in the players table in the database.
    )

def goalieSeasonLevelConverter(GoalieSeasonLevelObject: GoalieSeasonLevelObject, 
                               clubRowId: int, 
                               levelRowId: int, 
                               ageGroupRowId: int, 
                               seasonRowId: int) -> GoalieSeasonLevelRow:
    
    return GoalieSeasonLevelRow(
        # These are all ids pointing to rows in different tables. They are passed as parameters.
        clubId = clubRowId,         # Points to the row in "clubs" table - clubs.id
        levelId = levelRowId,       # Points to the row in "levels" table - levels.id
        ageGroupId = ageGroupRowId, # Points to the row in "age_groups" table - age_groups.id
        seasonId = seasonRowId,     # Points to the row in "goalie_seasons" table - goalie_seasons.id

        # These are the values from the GoalieSeasonLevelObject
        games = GoalieSeasonLevelObject.games,
        played = GoalieSeasonLevelObject.played,
        goalsAllowed = GoalieSeasonLevelObject.goalsAllowed,
        saves = GoalieSeasonLevelObject.saves,
        savePercentage = GoalieSeasonLevelObject.savePercentage
    )

def playerSeasonLevelConverter(PlayerSeasonLevelObject: PlayerSeasonLevelObject, 
                               clubRowId: int,
                               levelRowId: int,
                               ageGroupRowId: int,
                               seasonRowId: int) -> PlayerSeasonLevelRow:
    
    return PlayerSeasonLevelRow(
        # These are all ids pointing to rows in different tables. They are passed as parameters.
        clubId = clubRowId,         # Points to the row in "clubs" table - clubs.id
        levelId = levelRowId,       # Points to the row in "levels" table - levels.id
        ageGroupId = ageGroupRowId, # Points to the row in "age_groups" table - age_groups.id
        seasonId = seasonRowId,     # Points to the row in "player_seasons" table - player_seasons.id

        # These are the values from the PlayerSeasonLevelObject
        games = PlayerSeasonLevelObject.games,
        goals = PlayerSeasonLevelObject.goals,
        assists = PlayerSeasonLevelObject.assists,
        points = PlayerSeasonLevelObject.points,
        penaltyMinutes = PlayerSeasonLevelObject.penaltyMinutes
    )

def createClubRow(clubNameInput: str) -> ClubRow:
    return ClubRow(clubName = clubNameInput)

def createLevelRow(levelNameInput: str) -> LevelRow:
    return LevelRow(levelName = levelNameInput)

def createAgeGroupRow(ageGroupNameInput: str) -> AgeGroupRow:
    return AgeGroupRow(ageGroupName = ageGroupNameInput)
