from database.connection import createEmptyTables
from database.converters import playerConverter
from historical_scraper import oneGoalieTest

# Only do this if you want a fresh empty database
createEmptyTables()
Goalie = oneGoalieTest()
Player = playerConverter(Goalie)
print(Player)





# from historical_scraper import main, oneGoalieTest
# from database.app import main as dbMain

# Goalie = oneGoalieTest()

# print(Goalie)
# for season in Goalie.seasons:
#     print(season)
#     for seasonLevelStat in season.seasonLevelStats:
#         print(seasonLevelStat)

# dbMain()
