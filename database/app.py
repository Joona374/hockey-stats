from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv, find_dotenv

# Self made library that contains the declerative_base and Base models for all tables
from models import Base, Player

# Fetch the enviroment variables stored on the system
load_dotenv(find_dotenv())

# Fetch the enviroment variables stored on the system
DB_USER = os.getenv("MYSQL_USER")
DB_PW = os.getenv("MYSQL_PW")
DB_HOST = os.getenv("MYSQL_HOST")
DB_NAME = os.getenv("MYSQL_DB")

print(DB_USER, DB_PW, DB_HOST, DB_NAME)

# Build the connection string for the database
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PW}@{DB_HOST}/{DB_NAME}"

Engine = create_engine(DATABASE_URL, echo=True)

SessionClass = sessionmaker(bind=Engine)
Session = SessionClass()

Base.metadata.drop_all(Engine)
Base.metadata.create_all(Engine)

p1 = Player(sjlName="Sina Peisalo", birthYear=1996)
Session.add(p1)
Session.commit()