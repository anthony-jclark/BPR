
import os
import pickle
from argparse import ArgumentParser, ArgumentTypeError


def printGame(game):
    print " ", game["number"], " : ", game["date"], game["score"]


def analyzeAndRepair(gamedata):
    """Read through the file, look for missing games, and repair them."""
    game_num = 1
    new_games = []
    for game in gamedata["games"]:
        while game["number"] != game_num:
            print "Found a missing game number: ", game_num
            print "Here are previous 15 games:"
            for g in gamedata["games"][game_num - 15 - 1:game_num - 1]:
                printGame(g)
            print "And here are the next 15 games:"
            for g in gamedata["games"][game_num - 1:game_num + 15 - 1]:
                printGame(g)

            new_game = {"number": game_num}
            print "For the missing game, please give the following:"

            weekday = raw_input("Day of the week: ")
            month = raw_input("Month: ")
            monthday = raw_input("Day of the month: ")
            year = raw_input("Year: ")
            new_game["date"] = "{}, {} {}, {}".format(weekday, month,
                                                      monthday, year)
            team1 = raw_input("Team 1: ")
            team1scores = input("Team 1 scores (list): ")
            team2 = raw_input("Team 2: ")
            team2scores = input("Team 2 scores (list): ")
            new_game["teams"] = [team1, team2]
            new_game["score"] = {team1: team1scores, team2: team2scores}

            if len(team1scores) == len(team2scores):
                winner = input("Who won the shootout (team 1 or 2)?: ")
                team1shoot = 1 if winner == 1 else 0
                team2shoot = 1 if winner == 2 else 0
                new_game["shootout"] = {team1: team1shoot, team2: team2shoot}
            else:
                new_game["shootout"] = {team1: 0, team2: 0}

            new_games.append(new_game)

            game_num += 1
        game_num += 1

    # Add new games to list
    for ng in new_games:
        n = ng["number"]
        gamedata["games"] = gamedata["games"][:n - 1]\
            + [ng] + gamedata["games"][n - 1:]

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
            gamedata = pickle.load(datafile)
    except Exception:
        print("Could not load '{}' as pickle file.".format(args.file))
        exit()

    gamedata = analyzeAndRepair(gamedata)
    with open(args.file, 'wb') as datafile:
        pickle.dump(gamedata, datafile)


if __name__ == '__main__':
    main()
