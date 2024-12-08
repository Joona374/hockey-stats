import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

# Fetch the enviroment variables stored on the system
load_dotenv(find_dotenv())
DB_USER = os.getenv("MYSQL_USER")
DB_PW = os.getenv("MYSQL_PW")
DB_HOST = os.getenv("MYSQL_HOST")
DB_NAME = os.getenv("MYSQL_DB")

# Build the connection string for the database
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PW}@{DB_HOST}/{DB_NAME}"

Engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=Engine)

def createEmptyTables():
    """
    This is a development funciton.
    It's used to just reset the database and create the empty tables.
    """
    Base.metadata.drop_all(Engine)
    Base.metadata.create_all(Engine)