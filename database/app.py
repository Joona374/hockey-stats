# Import the necessary libraries
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv, find_dotenv

# Import the data container objects from the historical scraper
from historical_scraper.models.player import Player as PlayerObject
from historical_scraper.models.season import GoalieSeason, PlayerSeason, GoalieSeasonLevel, PlayerSeasonLevel
from historical_scraper.scraper import oneGoalieTest

# Import the self made library that contains the declerative_base and Base models for all tables
from database.models import Base, Player, GoalieSeason, GoalieSeasonLevel, PlayerSeason, PlayerSeasonLevel




# Fetch the enviroment variables stored on the system
load_dotenv(find_dotenv())
DB_USER = os.getenv("MYSQL_USER")
DB_PW = os.getenv("MYSQL_PW")
DB_HOST = os.getenv("MYSQL_HOST")
DB_NAME = os.getenv("MYSQL_DB")

# Build the connection string for the database
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PW}@{DB_HOST}/{DB_NAME}"

def createEmptyTables(Base: declarative_base, Engine: object):
    Base.metadata.drop_all(Engine)
    Base.metadata.create_all(Engine)

def main():
    Engine = create_engine(DATABASE_URL, echo=True)

    SessionClass = sessionmaker(bind=Engine)
    Session = SessionClass()

    createEmptyTables()

    Session.commit()
    Session.close()