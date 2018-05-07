#!/bin/python3

# DISCLAIMER: this code is not optimized at all

import random

nb_teams=8
nb_rounds=6
games_by_round=1
teams_by_game=4

# A game contains two set of teamIds ordered by position
# A round contains one or multiple games
def displayTournament(tournament):
    for round_idx in range(len(tournament)):
        r = tournament[round_idx]
        print("* Round " + str(round_idx))
        for game_idx in range(len(r)):
            print ("** Game " + str(game_idx)) 
            game = r[game_idx]
            print (str(game[0]) + " vs " + str(game[1]))

# Return a dictionary with idx -> nb_occurences at idx <= position_idx
def getOccurences(rounds, position_idx):
    dic = {}
    for team_id in range(nb_teams):
        dic[team_id] = 0
    for r in rounds:
        for game in r:
            for team in game:
                for idx in range(min(position_idx+1,len(team))):
                    dic[team[idx]] += 1
    return dic

# Return a dictionary mapping team_ids with the number of times they have been
# matched with 'team_id'
def getNbCoop(tournament, team_id):
    nb_coop = {}
    for other_team in range(nb_teams):
        nb_coop[other_team] = 0
    for r in tournament:
        for g in r:
            for side in g:
                if team_id in side:
                    for team in side:
                        nb_coop[team] += 1
    return nb_coop

# Return a dictionary mapping team_ids with the number of times they have been
# matched with 'team_id'
def getNbOpponents(tournament, team_id):
    nb_opp = {}
    for other_team in range(nb_teams):
        nb_opp[other_team] = 0
    for r in tournament:
        for g in r:
            for side_idx in range(2):
                if team_id in g[side_idx]:
                    other_side_idx = (side_idx + 1) % 2
                    for team in g[other_side_idx]:
                        nb_opp[team] += 1
    return nb_opp

# What is the cost of adding new_team to game with the given allies and
# opponents inside this tournament
# Aim: try to minimize the number of team couples as allies or against
def getCost(tournament, new_team, allies, opponents):
    nb_coop = getNbCoop(tournament, new_team)
    nb_opp = getNbOpponents(tournament, new_team)
    for team in allies:
        nb_coop[team] += 1
    for team in opponents:
        nb_opp[team] += 1
    cost = 0
    for team in range(nb_teams):
        if team != new_team:
            coop = nb_coop[team]
            opp = nb_opp[team]
            avg = (coop + opp) / 2.0
            cost += coop ** 2 + opp ** 2
    return cost

# Return the list of teams allowed to be placed at positiion_idx for this round
# Constraint: Only teams which have appeared the least times at a position index
# lower or equal to position_idx are allowed to be placed here
def allowedTeams(rounds, position_idx):
    occ_by_team = getOccurences(rounds,position_idx)
    min_occ = nb_rounds# Max score per round: 1
    allowed_teams = []
    for team_id in range(nb_teams):
        if occ_by_team[team_id] == min_occ:
            allowed_teams += [team_id]
        elif occ_by_team[team_id] < min_occ:
            # Reset list of allowed teams if we found a team who played less
            allowed_teams = [team_id]
            min_occ = occ_by_team[team_id]
    return allowed_teams

def teamsInRound(r):
    teams = []
    for game in r:
        for side in game:
            for team in side:
                teams += [team]
    return teams

def createEmptyGame():
    return [[],[]]

#TODO: stop adding teams if there is not enough teams to fill the rounds
def getNextRound(rounds):
    current_round = []
    for game_id in range(games_by_round):
        current_round += [createEmptyGame()]
    # Ordering placement of teams by pos_idx
    for pos_idx in range(teams_by_game):
        for game_id in range(games_by_round):
            for side in range(2):# For every side of the elements
                allowed_teams = allowedTeams(rounds + [current_round], pos_idx)
                random.shuffle(allowed_teams)
                filtered_teams = []
                teams_in_round = teamsInRound(current_round)
                for team in allowed_teams:
                    if team not in teams_in_round:
                        filtered_teams += [team]
                # TODO: sometimes, the team which has played the least is already playing
                # -> need_fix
                if len(filtered_teams) == 0:
                    print("Failed to finish creating round")
                    print("Actual tournament: ")
                    displayTournament(rounds)
                    print("Current round: " + str(current_round))
                    print("AllowedTeams: " + str(allowed_teams))
                    print("occurences(...," + str(pos_idx) + ")")
                    print("Modified tournament:")
                    displayTournament(rounds + [current_round])
                    print(getOccurences(rounds + [current_round], pos_idx))
                    exit(1)
                # Computing opponents and allies
                opp_side = (side +1) % 2
                allies = current_round[game_id][side]
                opponents = current_round[game_id][opp_side]
                # Getting filtered team with lowest cost
                best_team_id = filtered_teams[0]
                best_cost = getCost(rounds, best_team_id, allies, opponents)
                for filtered_team_idx in range(1,len(filtered_teams)):
                    team_id = filtered_teams[filtered_team_idx]
                    cost = getCost(rounds, team_id, allies, opponents)
                    if (cost < best_cost):
                        best_team_id = team_id
                        best_cost = cost
                current_round[game_id][side] += [best_team_id]
    return current_round

def createTournament():
    tournament = []
    for round_id in range(nb_rounds):
        tournament += [getNextRound(tournament)]
    return tournament

# Return a dictonary with for each team: the number of times it played at each
# position
def getPositionStats(tournament):
    dic = {}
    for team_id in range(nb_teams):
        dic[team_id] = []
        for pos_idx in range(teams_by_game):
            dic[team_id] += [0]
    for r in tournament:
        for game in r:
            for side in game:
                for pos_idx in range(len(side)):
                    team_id = side[pos_idx]
                    dic[team_id][pos_idx] += 1
    return dic

def displayPositionStats(pos_stats):
    for (team_id, team_stats) in pos_stats.items():
        print("%02d -> %d games: detail %s"  % (team_id,sum(team_stats), str(team_stats)))


# Return a dictonary with for each team, the number of time it played
# with/against each other team
def getMatesStats(tournament):
    dic = {}
    for team_id in range(nb_teams):
        dic[team_id] = {}
        for other_team_id in range(nb_teams):
            if other_team_id != team_id:
                dic[team_id][other_team_id] = [0,0]#[with/against]
    for r in tournament:
        for game in r:
            # Count partnerships
            for side_idx in range(2):
                with_side = game[side_idx]
                opp_side = game[(side_idx + 1) % 2]
                for team_id in with_side:
                    for with_id in with_side:
                        if (team_id < with_id):# Avoid to count twice partners (or self)
                            dic[team_id][with_id][0] += 1
                            dic[with_id][team_id][0] += 1
                    for opp_id in opp_side:
                        if (team_id < opp_id):# Avoid to count twice opponents
                            dic[team_id][opp_id][1] += 1
                            dic[opp_id][team_id][1] += 1
    return dic

def displayMatesStats(mates_stats):
    for team_id in range(nb_teams):
        for other_team_id in range(team_id+1, nb_teams):
            w = mates_stats[team_id][other_team_id][0]
            a = mates_stats[team_id][other_team_id][1]
            print("(%02d,%02d) : %d with / %d against"  % (team_id, other_team_id, w, a))

tournament = createTournament()
displayTournament(tournament)

pos_stats = getPositionStats(tournament)
displayPositionStats(pos_stats)

mates_stats = getMatesStats(tournament)
displayMatesStats(mates_stats)
