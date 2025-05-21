import json
import requests as rq


def init(team_id):
    global id_score
    while len(id_score) <= team_id:
        id_score.append(dict())
    if not 'delta' in id_score[team_id].keys():
        id_score[team_id]['delta'] = 0
        id_score[team_id]['wins'] = 0
        id_score[team_id]['losses'] = 0


token_map = json.load(open("Token.json"))
token = token_map["Token"]
header = {"Authorization": token}

url = 'https://lksh-enter.ru/matches'
matches = rq.get(url, headers=header)

url = 'https://lksh-enter.ru/teams'
teams = rq.get(url, headers=header)


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

cnt=0
for pl_id in players_id:
    cnt+=1
    if cnt>=10:break
    url = 'https://lksh-enter.ru/players/' + str(pl_id)
    player = rq.get(url, headers=header)
    name = player.json()['name'] + ' ' + player.json()['surname']
    players.append(name)
    #print(pl_id,name)

players = sorted(list(set(players)))
for player in players:
    print(player)


#cnt=0
for cur in matches.json():
    #cnt+=1
    #if cnt>=5:break
    #print(cur)
    team1_score = cur['team1_score']
    team2_score = cur['team2_score']
    team1_id = cur['team1']
    team2_id = cur['team2']

    init(team1_id)
    init(team2_id)

    id_score[team1_id]['delta'] += (team1_score - team2_score)
    id_score[team2_id]['delta'] += (team2_score - team1_score)
    if team1_score > team2_score:
        id_score[team1_id]['wins'] += 1
        id_score[team2_id]['losses'] += 1
    elif team1_score < team2_score:
        id_score[team1_id]['losses'] += 1
        id_score[team2_id]['wins'] += 1

for cur in teams.json():
    team_id=cur['id']
    init(team_id)
    id_score[team_id]['players']=cur['players']

while True:
    question = input().split()
    if question[0] == 'stats?':
        name = question[1]
        if len(name) < 2:
            print(0, 0, 0)
        name = name[1:-1]

        if not name in team_to_id.keys():
            print(0, 0, 0)
            continue
        team_id = team_to_id[name]
        wins = id_score[team_id]['wins']
        losses = id_score[team_id]['losses']
        delta = id_score[team_id]['delta']
        print(wins, losses, delta)
    elif question[0]=='versus?':
        id_1=question[1]
        id_2=question[2]
        answer=0
        for cur in matches.json():
            team1_id = cur['team1']
            team2_id = cur['team2']
            team1_players=id_score[team1_id]['players']
            team2_players=id_score[team2_id]['players']
            team1_id1= id_1 in team1_players
            team1_id2= id_2 in team1_players
            team2_id1= id_1 in team2_players
            team2_id2= id_2 in team2_players
            if team1_id1 and team2_id2:
                answer+=1
            elif team1_id2 and team2_id1:
                answer+=1
        print(answer)