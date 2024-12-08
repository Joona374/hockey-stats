

from database.connection import SessionLocal
from database.models import Player as PlayerRow, GoalieSeason as GoalieSeasonRow, PlayerSeason as PlayerSeasonRow, PlayerSeasonLevel as PlayerSeasonLevelRow, GoalieSeasonLevel as GoalieSeasonLevelRow, Club as ClubRow, Level as LevelRow, AgeGroup as AgeGroupRow
from historical_scraper.models.player import Player as PlayerObject
from database.converters import playerConverter, goalieSeasonConverter, playerSeasonConverter, playerSeasonLevelConverter, goalieSeasonLevelConverter, createClubRow, createLevelRow, createAgeGroupRow

def checkIfClubExists(ClubName: str, Session: object) -> int:
    try:
        Row = Session.query(ClubRow).filter(ClubRow.clubName == ClubName).one()
        return Row.id
    except Exception:
        Club = createClubRow(ClubName)
        Session.add(Club)
        Session.flush()
        print(f"\nCreated a new club row for {ClubName}\n")
        return Club.id
    
def checkIfLevelExists(LevelName: str, Session: object) -> int:
    try:
        Row = Session.query(LevelRow).filter(LevelRow.levelName == LevelName).one()
        return Row.id
    except Exception:
        Level = createLevelRow(LevelName)
        Session.add(Level)
        Session.flush()
        print(f"\nCreated a new level row for {LevelName}\n")
        return Level.id
    
def checkIfAgeGroupExists(AgeGroupName: str, Session: object) -> int:
    try:
        Row = Session.query(AgeGroupRow).filter(AgeGroupRow.ageGroupName == AgeGroupName).one()
        return Row.id
    except Exception:
        AgeGroup = createAgeGroupRow(AgeGroupName)
        Session.add(AgeGroup)
        Session.flush()
        print(f"\nCreated a new age group row for {AgeGroupName}\n")
        return AgeGroup.id



def writePlayerToDb(PlayerRow: PlayerRow, Session: object) -> int:
    Session.add(PlayerRow)
    Session.flush()
    return PlayerRow.id

def writeSeasonToDb(Season: object, PlayerId: int, Position: str, Session: object) -> int:    
    if Position == "Maalivahti":
        SeasonRow = goalieSeasonConverter(Season, PlayerId)
    elif Position == "Kenttäpelaaja":
        SeasonRow = playerSeasonConverter(Season, PlayerId)
    else:
        raise ValueError(f"Unsupported position: {Position} in writeSeasonToDb")

    Session.add(SeasonRow)
    Session.flush()
    return SeasonRow.id

def writeSeasonLevelToDb(SeasonLevelStat: object, SeasonId: int, PlayerObject: object, Session: object):
    clubId = checkIfClubExists(SeasonLevelStat.club, Session)
    levelId = checkIfLevelExists(SeasonLevelStat.level, Session)
    ageGroupId = checkIfAgeGroupExists(SeasonLevelStat.ageGroup, Session)
    
    if PlayerObject.position == "Maalivahti":
        SeasonLevelStatRow = goalieSeasonLevelConverter(SeasonLevelStat, SeasonId, clubId, levelId, ageGroupId, PlayerObject.id)
    elif PlayerObject.position == "Kenttäpelaaja":
        SeasonLevelStatRow = playerSeasonLevelConverter(SeasonLevelStat, SeasonId, clubId, levelId, ageGroupId, PlayerObject.id)
    else:
        raise ValueError(f"Unsupported position: {PlayerObject.position} in writeSeasonLevelToDb")

    Session.add(SeasonLevelStatRow)
    Session.flush()

def writeEntirePlayerToDb(PlayerObject: PlayerObject):
    Session = SessionLocal()
    PlayerRow = playerConverter(PlayerObject)
    PlayerId = writePlayerToDb(PlayerRow, Session)
    PlayerObject.id = PlayerId

    for key, value in vars(PlayerObject).items():
        print(f"{key}: {value}")

    for Season in PlayerObject.seasons:
        SeasonId = writeSeasonToDb(Season, PlayerId, PlayerObject.position, Session)

        for SeasonLevelStat in Season.seasonLevelStats:
            writeSeasonLevelToDb(SeasonLevelStat, SeasonId, PlayerObject, Session)


    Session.commit()
    Session.close()
