def goaliesToDict(Goalies: list) -> dict:
    GoaliesDict = {}
    for goalie in Goalies:
        GoaliesDict[goalie.id] = goalie
    return GoaliesDict

def playersToDict(Players: list) -> dict:
    PlayersDict = {}
    for player in Players:
        PlayersDict[player.id] = player
    return PlayersDict