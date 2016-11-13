#!../../.env/bin/python

import pickle
import os
import json
from datetime import datetime, timedelta
from argparse import ArgumentParser, ArgumentTypeError

# Constants
num_teams = 30


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


# def shrinkData(teams, data, season):
#     """Take the data and shrink it for a json dump."""
#     resultlabels = ["SOW", "SOL", "OTW", "OTL", "WIN", "LOS"]
#     resids = {r: i for i, r in enumerate(resultlabels)}
#     teamids = {n: i for i, n in enumerate(sorted(list(teams)))}
#     shrunk = []
#     for d in data:
#         item = {"date": d["date"], "games": []}
#         for g in d["results"]:
#             item["games"].append((teamids[g[0]], resids[g[1]]))
#         shrunk.append(item)
#     return {
#         "teams": teamids, "outcomes": resids,
#         "season": season, "results": shrunk}


def formatData(gamedata, season):
    """Take the raw game data and format it for plotting."""

    # Set to check team names (should be 30 total)
    teams = set()

    # Team data
    datedata = []

    # Range of dates
    date_start = gamedata[0]["date"]
    date_end = gamedata[-1]["date"]

    g = 0
    for d in daterange(date_start, date_end + timedelta(1)):
        datestr = "{}-{:0>2}-{:0>2}".format(d.year, d.month, d.day)
        todaydata = {"date": datestr, "results": []}
        while g < len(gamedata) and gamedata[g]["date"] == d:
            game = gamedata[g]
            winner, loser = game["winner"], game["loser"]
            teams.update((winner, loser))

            if game["shootout"]:
                winnerout = "SOW"
                loserout = "SOL"
            elif game["overtime"]:
                winnerout = "OTW"
                loserout = "OTL"
            else:
                winnerout = "WIN"
                loserout = "LOS"

            todaydata["results"].append((winner, winnerout))
            todaydata["results"].append((loser, loserout))
            g += 1
        datedata.append(todaydata)

    assert len(teams) == num_teams
    # ds = (date_start.year, date_start.month, date_start.day)
    # de = (date_end.year, date_end.month, date_end.day)

    return {
        "first_date": str(date_start),
        "last_date": str(date_end),
        "teams": list(teams),
        "season": season,
        "data": datedata}


def formatScores(gamedata):
    """Calculate team points from scores."""
    new_gamedata = []
    for game in gamedata:
        team1, team2 = game["teams"][0], game["teams"][1]

        scores1, scores2 = game["score"][team1], game["score"][team2]
        overtime = 4 in (scores1 + scores2)

        shootout = len(scores1) == len(scores2)
        team1SO = game["shootout"][team1] > game["shootout"][team2]

        score1 = len(scores1) + 1 if shootout and team1SO else len(scores1)
        score2 = len(scores2) + 1 if shootout and not team1SO else len(scores2)

        new_gamedata.append({
            "date": game["date"],
            "score": {team1: score1, team2: score2},
            "winner": team1 if score1 > score2 else team2,
            "loser": team1 if score1 < score2 else team2,
            "loserpoint": 1 if (overtime or shootout) else 0,
            "overtime": overtime,
            "shootout": shootout
        })

    return new_gamedata


def formatDates(gamedata):
    """Convert string dates into date objects."""
    for game in gamedata:
        game["date"] = datetime.strptime(game["date"], "%A, %B %d, %Y").date()
    return gamedata


def parseFile(arg):
    """Check for valid input file from CL."""
    if not os.path.isfile(arg):
        raise ArgumentTypeError("'{}' is not a valid file.".format(arg))
    return arg


def main():
    argparser = ArgumentParser()
    argparser.add_argument("file",
                           help="a file to analyze and repair",
                           type=parseFile)

    args = argparser.parse_args()
    try:
        with open(args.file, 'rb') as datafile:
            data = pickle.load(datafile)
            season = data["season"]
            gamedata = data["games"]
    except Exception:
        print("Could not load '{}' as pickle file.".format(args.file))
        exit()

    gamedata = formatDates(gamedata)
    gamedata = formatScores(gamedata)
    datedata = formatData(gamedata, season)
    # packeddata = shrinkData(teams, datedata, season)

    print json.dumps(datedata)
    # print json.dumps(datedata, sort_keys=True,
    #                  indent=4, separators=(',', ': '))


if __name__ == '__main__':
    main()
