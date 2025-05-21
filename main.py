import json
import requests as rq
from functions import add_start_action_to_logs
from functions import check_correct
from functions import init
from functions import add_question_to_logs

add_start_action_to_logs()

token_map = json.load(open("Token.json"))
token = token_map["Token"]
header = {"Authorization": token}

url = 'https://lksh-enter.ru/matches'
matches = rq.get(url, headers=header)
check_correct(matches)

url = 'https://lksh-enter.ru/teams'
teams = rq.get(url, headers=header)
check_correct(teams)

team_to_id = dict()
id_to_team = dict()
players_id = []
players = []
id_score = []

for cur in teams.json():
    id = cur['id']
    name = cur['name']
    team_to_id[name] = id
    id_to_team[id] = name
    for pl_id in cur['players']:
        players_id.append(pl_id)


cnt = 0
for pl_id in players_id:

    # ограничение на число выводимых игроков (спрашивать всех слишком долго):
    cnt += 1
    if cnt >= 5: break

    url = 'https://lksh-enter.ru/players/' + str(pl_id)
    player = rq.get(url, headers=header)
    check_correct(player)
    name = player.json()['name'] + ' ' + player.json()['surname']
    players.append(name)
    # print(pl_id,name)

players = sorted(list(set(players)))
for player in players:
    print(player)

# cnt = 0
for cur in matches.json():
    # cnt += 1
    # if cnt >= 3: break
    # print(cur)
    team1_score = cur['team1_score']
    team2_score = cur['team2_score']
    team1_id = cur['team1']
    team2_id = cur['team2']

    init(team1_id, id_score)
    init(team2_id, id_score)

    id_score[team1_id]['delta'] += (team1_score - team2_score)
    id_score[team2_id]['delta'] += (team2_score - team1_score)
    if team1_score > team2_score:
        id_score[team1_id]['wins'] += 1
        id_score[team2_id]['losses'] += 1
    elif team1_score < team2_score:
        id_score[team1_id]['losses'] += 1
        id_score[team2_id]['wins'] += 1

for cur in teams.json():
    team_id = cur['id']
    init(team_id, id_score)
    id_score[team_id]['players'] = cur['players']


# cur = matches.json()[1]
# print(cur, id_score[cur['team1']]['players'], id_score[cur['team2']]['players'])
# print(id_to_team[cur['team1']], id_to_team[cur['team2']])

while True:
    question_str = input()
    question = question_str.split()
    if question[0] == 'stats?':
        pos = 8
        name = question_str[pos:len(question_str) - 1]

        if not name in team_to_id.keys():
            add_question_to_logs(question[0], name, [0, 0, 0])
            print(0, 0, 0)
            continue

        team_id = team_to_id[name]
        wins = id_score[team_id]['wins']
        losses = id_score[team_id]['losses']
        delta = id_score[team_id]['delta']

        data_answer = {'wins': wins, 'losses': losses, 'delta': delta}
        data = {'name': name}
        add_question_to_logs(question[0], data, data_answer)

        print(wins, losses, delta)
    elif question[0] == 'versus?':
        id_1 = int(question[1])
        id_2 = int(question[2])
        answer = 0
        data_matches = []
        for cur in matches.json():
            team1_id = cur['team1']
            team2_id = cur['team2']
            team1_players = id_score[team1_id]['players']
            team2_players = id_score[team2_id]['players']
            team1_id1 = id_1 in team1_players
            team1_id2 = id_2 in team1_players
            team2_id1 = id_1 in team2_players
            team2_id2 = id_2 in team2_players
            if (team1_id1 and team2_id2) or (team1_id2 and team2_id1):
                answer += 1
                current_match_info = cur
                current_match_info['team1_name'] = id_to_team[team1_id]
                current_match_info['team2_name'] = id_to_team[team2_id]
                current_match_info['team1_players'] = id_score[team1_id]['players']
                current_match_info['team2_players'] = id_score[team2_id]['players']
                data_matches.append(current_match_info)

        data = {'id_1': id_1, 'id_2': id_2}
        data_answer = {'answer': answer, 'matches': data_matches}
        add_question_to_logs(question[0], data, data_answer)
        print(answer)
    else:
        add_question_to_logs(question[0], "incorrect question", "incorrect question")
        print("incorrect question")
