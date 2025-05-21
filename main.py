import json
import requests as rq
from datetime import datetime

def init(team_id):
    global id_score
    while len(id_score) <= team_id:
        id_score.append(dict())
    if not 'delta' in id_score[team_id].keys():
        id_score[team_id]['delta'] = 0
        id_score[team_id]['wins'] = 0
        id_score[team_id]['losses'] = 0

def check_correct(resp):
    if not isinstance(resp, rq.Response):
        print("Error. Maybe, server returned incorrect answer or bad connection")
    else:
        status=resp.status_code
        if status>=300:
            print(status,'Error')
            if status==401:
                print("Maybe token is invalid or empty")

            with open('logs.json','r') as f:
                log=json.load(f)
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            error_data={"type":"response error","status code":status,"time":current_time}
            log.append(error_data)
            with open('logs.json','w') as f:
                json.dump(log,f,indent=4)
            exit(0)

def add_question_to_logs(question,data,answer):
    with open('logs.json','r') as f:
        log=json.load(f)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    question_data={"type":"user question","name":question,"data":data,"answer":answer,"time":current_time}
    log.append(question_data)
    with open('logs.json','w') as f:
        json.dump(log,f,indent=4)

def add_start_action_to_logs():
    with open('logs.json','r') as f:
        log=json.load(f)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    start_data={"type":"start of programm","time":current_time}
    log.append(start_data)
    with open('logs.json','w') as f:
        json.dump(log,f,indent=4)


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
    cnt += 1
    if cnt >= 3: break
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
    team_id = cur['id']
    init(team_id)
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
            add_question_to_logs(question[0],name,[0,0,0])
            print(0, 0, 0)
            continue

        team_id = team_to_id[name]
        wins = id_score[team_id]['wins']
        losses = id_score[team_id]['losses']
        delta = id_score[team_id]['delta']

        ans={'wins':wins,'losses':losses,'delta':delta}
        data={'name':name}
        add_question_to_logs(question[0],data,ans)

        print(wins, losses, delta)
    elif question[0] == 'versus?':
        id_1 = int(question[1])
        id_2 = int(question[2])
        answer = 0
        for cur in matches.json():
            team1_id = cur['team1']
            team2_id = cur['team2']
            team1_players = id_score[team1_id]['players']
            team2_players = id_score[team2_id]['players']
            team1_id1 = id_1 in team1_players
            team1_id2 = id_2 in team1_players
            team2_id1 = id_1 in team2_players
            team2_id2 = id_2 in team2_players
            if team1_id1 and team2_id2:
                answer += 1
            elif team1_id2 and team2_id1:
                answer += 1
        
        data={'id_1':id_1,'id_2':id_2}
        add_question_to_logs(question[0],data,{'answer':answer})
        print(answer)
    else:
        add_question_to_logs(question[0],"incorrect question","incorrect question")
        print("incorrect question")