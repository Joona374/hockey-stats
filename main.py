from database.connection import createEmptyTables
from database.converters import playerConverter
from database.writer import writeEntirePlayerToDb
from database.reader import getDbContents
from historical_scraper import oneGoalieTest, onePlayerTest, main as scraperMain

### THESE ARE FOR UNDER CONSTRUCTION TESTING ###

dbDict = getDbContents()        # Queries the database and returns all contents of "players", "clubs", "levels" and "age_groups" tables.
# createEmptyTables()             # Only do this if you want a fresh empty database

# Goalie = oneGoalieTest()      # Test function that returns only 1 Goalie
# Player = onePlayerTest()      # Test function that returns only 1 Player
# writeEntirePlayerToDb(Player) # Write the player to the database

Players = scraperMain()
for Player, PlayerObject in Players.items():
    writeEntirePlayerToDb(PlayerObject)   # Writes the goalie (or any player) to the database
