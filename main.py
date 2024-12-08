from database.connection import createEmptyTables
from database.converters import playerConverter
from database.writer import writeEntirePlayerToDb
from historical_scraper import oneGoalieTest, main


### THESE ARE FOR UNDER CONSTRUCTION TESTING ###

createEmptyTables()             # Only do this if you want a fresh empty database
Goalie = oneGoalieTest()        # Test function that returns only 1 Goalie
Players = main()
writeEntirePlayerToDb(Goalie)   # Writes the goalie (or any player) to the database
