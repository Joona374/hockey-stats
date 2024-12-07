# This class is used to just collect and hold all the data. 
# seasonRosterHtmls will store the roster htmls before we start the parsing. It is a dict where the key is the year and the value is a string of html.
class Team:
    def __init__(self, name, teamId, sjlLink):
        self.name = name
        self.teamId = teamId
        self.sjlLink = sjlLink
        self.seasonRosterHtmls = {}

    def addSeasonRosterHtml(self, season, seasonRosterHtml):
        self.seasonRosterHtmls[season] = seasonRosterHtml
