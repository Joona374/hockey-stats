from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


# Define the base class
Base = declarative_base()

class Player(Base):
    """
    "players" table
    VALUES:
    - id = Column(Integer, primary_key=True, autoincrement=True)
    - sjlName = Column(String(255))
    - epName = Column(String(255))
    - sjlLink = Column(String(255))
    - position = Column(String(255))
    - birthYear = Column(Integer)

    - goalie_seasons = relationship("GoalieSeason", back_populates="player")
    - player_seasons = relationship("PlayerSeason", back_populates="player")
        
    """
    __tablename__ = 'players'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sjlName = Column(String(255))
    epName = Column(String(255))
    sjlLink = Column(String(255))
    position = Column(String(255))
    birthYear = Column(Integer)

    goalie_seasons = relationship("GoalieSeason", back_populates="player")
    player_seasons = relationship("PlayerSeason", back_populates="player")
    goalie_season_level = relationship("GoalieSeasonLevel", back_populates="player")
    player_season_level = relationship("PlayerSeasonLevel", back_populates="player")

    def __str__(self):
        """Returns a string representation of the Player object."""
        return f"{self.sjlName} {self.position} {self.birthYear} Player Row str representation"

class GoalieSeason(Base):
    """
    "goalie_seasons" table
    VALUES:
    - id = Column(Integer, primary_key=True, autoincrement=True)
    - year = Column(Integer)
    - games = Column(Integer)
    - played = Column(Integer)
    - goalsAllowed = Column(Integer)
    - timeOnIce = Column(Float)
    - gaa = Column(Float)
    - playerId = Column(Integer, ForeignKey('players.id'))

    - player = relationship("Player", back_populates="goalie_seasons")
    - seasonLevelStats = relationship("GoalieSeasonLevel", back_populates="season")
    """
    __tablename__ = 'goalie_seasons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer)
    games = Column(Integer)
    played = Column(Integer)
    goalsAllowed = Column(Integer)
    timeOnIce = Column(Float)
    gaa = Column(Float)
    playerId = Column(Integer, ForeignKey('players.id'))

    player = relationship("Player", back_populates="goalie_seasons")
    seasonLevelStats = relationship("GoalieSeasonLevel", back_populates="season")

class PlayerSeason(Base):
    """
    "player_seasons" table
    VALUES:
    - id = Column(Integer, primary_key=True, autoincrement=True)
    - year = Column(Integer)
    - games = Column(Integer)
    - goals = Column(Integer)
    - assists = Column(Integer)
    - points = Column(Integer)
    - penaltyMinutes = Column(Integer)
    - ppGoals = Column(Integer)
    - shGoals = Column(Integer)
    - soGoals = Column(Integer)

    - player = relationship("Player", back_populates="player_seasons")
    - seasonLevelStats = relationship("PlayerSeasonLevel", back_populates="season")
    """
    __tablename__ = "player_seasons"

    id = Column(Integer, primary_key=True, autoincrement=True)
    year = Column(Integer)
    games = Column(Integer)
    goals = Column(Integer)
    assists = Column(Integer)
    points = Column(Integer)
    penaltyMinutes = Column(Integer)
    ppGoals = Column(Integer)
    shGoals = Column(Integer)
    soGoals = Column(Integer)
    playerId = Column(Integer, ForeignKey('players.id')) 

    player = relationship("Player", back_populates="player_seasons")
    seasonLevelStats = relationship("PlayerSeasonLevel", back_populates="season")

    
class GoalieSeasonLevel(Base):
    """
    "goalie_season_level" table
    VALUES:
    - id = Column(Integer, primary_key=True, autoincrement=True)
    - club_id = Column(Integer, ForeignKey("clubs.id"))
    - level_id = Column(Integer, ForeignKey("levels.id"))
    - ageGroup_id = Column(Integer, ForeignKey("age_groups.id"))

    - games = Column(Integer)
    - played = Column(Integer)
    - goalsAllowed = Column(Integer)
    - saves = Column(Integer)
    - savePercentage = Column(Float)
    - season_id = Column(Integer, ForeignKey("goalie_seasons.id"))

    - season = relationship("GoalieSeason", back_populates="seasonLevelStats")
    - club = relationship("Club", back_populates="goalieSeasonLevels")
    - level = relationship("Level", back_populates="goalieSeasonLevels")
    - ageGroup = relationship("AgeGroup", back_populates="goalieSeasonLevels")
    """
    __tablename__ = "goalie_season_level"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clubId = Column(Integer, ForeignKey("clubs.id"))
    levelId = Column(Integer, ForeignKey("levels.id"))
    ageGroupId = Column(Integer, ForeignKey("age_groups.id"))

    games = Column(Integer)
    played = Column(Integer)
    goalsAllowed = Column(Integer)
    saves = Column(Integer)
    savePercentage = Column(Float)
    seasonId = Column(Integer, ForeignKey("goalie_seasons.id"))
    playerId = Column(Integer, ForeignKey('players.id'))

    player = relationship("Player", back_populates="goalie_season_level")
    season = relationship("GoalieSeason", back_populates="seasonLevelStats")
    club = relationship("Club", back_populates="goalieSeasonLevel")
    level = relationship("Level", back_populates="goalieSeasonLevel")
    ageGroup = relationship("AgeGroup", back_populates="goalieSeasonLevel")

class PlayerSeasonLevel(Base):
    """
    "player_season_level" table
    VALUES:
    - id = Column(Integer, primary_key=True, autoincrement=True)
    - club_id = Column(Integer, ForeignKey("clubs.id"))
    - level_id = Column(Integer, ForeignKey("levels.id"))
    - ageGroup_id = Column(Integer, ForeignKey("age_groups.id"))

    - games = Column(Integer)
    - goals = Column(Integer)
    - assists = Column(Integer)
    - points = Column(Integer)
    - penaltyMinutes = Column(Integer)

    - season = relationship("PlayerSeason", back_populates="seasonLevelStats")
    - club = relationship("Club", back_populates="playerSeasonLevels")
    - level = relationship("Level", back_populates="playerSeasonLevels")
    - ageGroup = relationship("AgeGroup", back_populates="playerSeasonLevels")
    """
    __tablename__ = "player_season_level"

    id = Column(Integer, primary_key=True, autoincrement=True)
    club_id = Column(Integer, ForeignKey("clubs.id"))
    level_id = Column(Integer, ForeignKey("levels.id"))
    ageGroup_id = Column(Integer, ForeignKey("age_groups.id"))

    games = Column(Integer)
    goals = Column(Integer)
    assists = Column(Integer)
    points = Column(Integer)
    penaltyMinutes = Column(Integer)
    seasonId = Column(Integer, ForeignKey("player_seasons.id"))
    playerId = Column(Integer, ForeignKey('players.id')) 

    player = relationship("Player", back_populates="player_season_level")
    season = relationship("PlayerSeason", back_populates="seasonLevelStats")
    club = relationship("Club", back_populates="playerSeasonLevel")
    level = relationship("Level", back_populates="playerSeasonLevel")
    ageGroup = relationship("AgeGroup", back_populates="playerSeasonLevel")

class Club(Base):
    """
    "clubs" table
    These rows are only created when encountering value, that is not already present in the table.
    VALUES:
    - id = Column(Integer, primary_key=True, autoincrement=True)
    - clubName = Column(String(255))

    - goalieSeasonLevel = relationship("GoalieSeasonLevel", back_populates="club")
    - playerSeasonLevel = relationship("PlayerSeasonLevel", back_populates="club")
    """
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clubName = Column(String(255))

    goalieSeasonLevel = relationship("GoalieSeasonLevel", back_populates="club")
    playerSeasonLevel = relationship("PlayerSeasonLevel", back_populates="club")


class Level(Base):
    """
    "level" table
    These rows are only created when encountering value, that is not already present in the table.
    VALUES:
    - id = Column(Integer, primary_key=True, autoincrement=True)
    - levelName = Column(String(255))
    """
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, autoincrement=True)
    levelName = Column(String(255))

    goalieSeasonLevel = relationship("GoalieSeasonLevel", back_populates="level")
    playerSeasonLevel = relationship("PlayerSeasonLevel", back_populates="level")

class AgeGroup(Base):
    """
    "age_groups" table
    These rows are only created when encountering value, that is not already present in the table.
    VALUES:
    - id = Column(Integer, primary_key=True, autoincrement=True)
    - ageGroupName = Column(String(255))
    """
    __tablename__ = "age_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ageGroupName = Column(String(255))

    goalieSeasonLevel = relationship("GoalieSeasonLevel", back_populates="ageGroup")
    playerSeasonLevel = relationship("PlayerSeasonLevel", back_populates="ageGroup")