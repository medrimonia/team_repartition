# DISCLAIMER: this code is not optimized at all

nb_teams=20
nb_rounds=6
games_by_round=2
teams_by_game=5#Kid size

# A game contains two set of teamIds ordered by position
# A round contains one or multiple games

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
    for team_id in range(nb_teams):
        nb_coop[team_id] = 0
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
    for team_id in range(nb_teams):
        nb_opp[team_id] = 0
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
            cost += nb_coop[team] ** 2 + nb_opp[team] ** 2
    return cost

# Return the list of teams allowed to be placed at positiion_idx for this round
# Constraint: Only teams which have appeared the least times at a position index
# lower or equal to position_idx are allowed to be placed here
def allowedTeams(rounds, position_idx):
    games_by_team = getOccurences(rounds, position_idx)
    min_occurences = nb_rounds# A team cannot play more than once by round
    allowed_teams = []
    for team_id in range(nb_teams):
        if games_by_team[team_id] == min_occurences:
            allowed_teams += [team_id]
        elif games_by_team[team_id] < min_occurences:
            # Reset list of allowed teams if we found a team who played less
            allowed_teams = [team_id]
            min_occurences = games_by_team[team_id]
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
                filtered_teams = []
                teams_in_round = teamsInRound(current_round)
                for team in allowed_teams:
                    if team not in teams_in_round:
                        filtered_teams += [team]
                # TODO: sometimes, the team which has played the least is already playing
                # -> need_fix
                if len(filtered_teams) == 0:
                    print("Failed to finish creating round")
                    print("Current round: " + str(current_round))
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

def displayTournament(tournament):
    for round_idx in range(len(tournament)):
        r = tournament[round_idx]
        print("* Round " + str(round_idx))
        for game_idx in range(len(r)):
            print ("** Game " + str(game_idx)) 
            game = r[game_idx]
            print (str(game[0]) + " vs " + str(game[1]))

exampleGame1 = [[1,2],[3,4]]
exampleGame2 = [[3,2],[4,0]]
exampleGame3 = [[0,1],[2,4]]

exampleRound1 = [exampleGame1, exampleGame2]
exampleRound2 = [exampleGame3]

rounds = [exampleRound1, exampleRound2]

#print getOccurences(rounds, 1)
#print teamsInRound(exampleRound2)

displayTournament(createTournament())
