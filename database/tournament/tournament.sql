-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


-- delete the exist tournament database
DROP DATABASE IF EXISTS tournament;

-- create the new tournament database
CREATE DATABASE tournament;
\c tournament;

-- Create players table with name and id
CREATE TABLE Players (name text, playerid serial PRIMARY KEY);

-- Create matches table which record the winner and loser for each match
CREATE TABLE Matches (winner integer REFERENCES Players(playerid),
                      loser integer REFERENCES Players(playerid),
                      matchid serial PRIMARY KEY);

-- The number of players view
CREATE VIEW CountPlayer AS SELECT count(*) as num FROM Players;

-- Player standing
CREATE VIEW PlayerStand AS SELECT Players.playerid as playerid,
                                Players.name as name,
                                (SELECT count(*) FROM Matches
                                 WHERE Players.playerid = Matches.winner) as wins,
                                (SELECT count(*) FROM matches
                                 WHERE Players.playerid = Matches.winner OR
                                        Players.playerid = Matches.loser) as matches
                                FROM Players LEFT JOIN Matches on
                                (Players.playerid = Matches.winner or Players.playerid = Matches.loser)
                                ORDER BY wins DESC;

