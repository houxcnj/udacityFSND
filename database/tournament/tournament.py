#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import math


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()

    c.execute("DELETE FROM Matches;")

    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()

    c.execute("DELETE FROM Players;")

    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM Countplayer;")

    # Retrieve the first row of the result set
    res = c.fetchone()[0]

    conn.close()

    return res


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()

    # To avoid the name with the "'"
    name = name.replace("'", "''")

    # Insert the player into Players table
    c.execute("INSERT INTO Players VALUES ('%s')" % name)

    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()

    c.execute("SELECT * FROM PlayerStand;")

    # Retrieve the all result as a list of tuples
    standings = c.fetchall()

    res = []

    for standing in standings:

        # Because tuples are immutable, convert it to list
        standing = list(standing)
        # initial the table when there is no wins and matches
        if not standing[2]:
            standing[2] = 0

        if not standing[3]:
            standing[3] = 0

        # convert it back to tuple
        standing = tuple(standing)

        res.append(standing)

    conn.commit()
    conn.close()

    return res


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()

    query = "INSERT INTO Matches VALUES (%s, %s);"
    values = (winner, loser)
    c.execute(query, values)

    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    field = playerStandings()

    conn = connect()
    c = conn.cursor()

    # get this round
    c.execute("SELECT max(matches) FROM PlayerStand;")

    thisRound = c.fetchone()[0]

    conn.commit()
    conn.close()

    # based on swiss pairing, it needs log2(no. of players) rounds
    maxround = math.log(countPlayers(), 2)

    if thisRound <= maxround:

        res = []

        i = 0

        # pair the nearest two players
        while i < len(field):

            # create the game
            pair1 = list(field[i])
            pair2 = list(field[i+1])

            pair = (pair2[0], pair2[1], pair1[0], pair1[1])
            res.append(pair)

            i += 2

        return res

    else:
        print "GAME OVER!"

