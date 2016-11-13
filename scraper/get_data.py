#!./.env/bin/python

import os
import pickle
import traceback
from datetime import datetime, timedelta
from argparse import ArgumentParser, ArgumentTypeError

from nhlscrapi.games.game import Game, GameKey, GameType
from nhlscrapi.games.cumstats import Score

# Current month and year
today = datetime.today().date()
max_season = today.year if today.month < 8 else today.year + 1
min_season = 2016

# Constants
num_teams = 30
num_games = 82
max_game_num = num_teams * num_games / 2


def scrapeGameData(gamedata):
    """Scrape games data from NHL.com"""

    game_num = gamedata["games"][-1]["number"] + 1
    print "Starting to read game data at game number", str(game_num) + "."

    game_type = GameType.Regular
    while game_num <= max_game_num:
        game_key = GameKey(gamedata["season"], game_type, game_num)

        # define stat types that will be counted as the plays are parsed
        cum_stats = {'Score': Score()}
        game = Game(game_key, cum_stats=cum_stats)

        # http requests and processing are lazy
        # accumulators require play by play info so they parse the RTSS PBP
        game_data = {}

        try:
            game_data["number"] = game_num
            game_data["date"] = game.matchup["date"]
            game_data["teams"] = game.cum_stats['Score'].teams
            team1 = game_data["teams"][0]
            team2 = game_data["teams"][1]
            game_data["score"] = {team1: [], team2: []}
            game_data["shootout"] = game.cum_stats['Score'].shootout.total

            for play in game.cum_stats['Score'].tally:
                try:
                    play[team2]
                except KeyError:
                    game_data["score"][team1].append(play["period"])
                else:
                    game_data["score"][team2].append(play["period"])

        except (KeyboardInterrupt, SystemExit):
            raise

        except Exception as e:
            gamedate = datetime.strptime(gamedata["games"][-1]["date"],
                                         "%A, %B %d, %Y").date()

            if gamedate >= today - timedelta(days=1):
                print "Finished processing games."
                break
            else:
                print "\n***"
                print "Missing game data for game number", str(game_num) + "."
                print e
                print traceback.print_exc()
                print "***\n"

        else:
            print "Game number ", game_num, " : ", game_data
            gamedata["games"].append(game_data)

        game_num += 1
    return gamedata


def parseSeason(arg):
    """Check for valid numbers for seasons on CL input."""
    try:
        val = int(arg)
    except ValueError:
        raise ArgumentTypeError("'{}' is not an integer.".format(arg))
    else:
        if val > max_season or val < min_season:
            raise ArgumentTypeError("year '{}' is out of range.".formate(arg))
    return val


def parseFile(arg):
    """Check for valid input file from CL."""
    if not os.path.isfile(arg):
        raise ArgumentTypeError("'{}' is not a valid file.".format(arg))
    return arg


def main():
    argparser = ArgumentParser()
    argparser.add_argument("-y", "--year",
                           help="year in which the regular season ends",
                           type=parseSeason)
    argparser.add_argument("-f", "--file",
                           help="a file to which this program will append",
                           type=parseFile)

    args = argparser.parse_args()
    if not args.year:
        season = max_season
    else:
        season = args.year
    if not args.file:
        fname = "{}-{}_season.pickle".format(season - 1, season)
        gamedata = {"season": season, "games": []}
    else:
        fname = args.file
        try:
            with open(fname, 'rb') as datafile:
                gamedata = pickle.load(datafile)
        except Exception:
            print("Could not load '{}' as pickle file.".format(fname))
            exit()
        else:
            if gamedata["season"] != season:
                print("Seasons do not match.")
                exit()

    gamedata = scrapeGameData(gamedata)
    with open(fname, 'wb') as datafile:
        pickle.dump(gamedata, datafile)


if __name__ == '__main__':
    main()
