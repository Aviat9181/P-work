import json
import requests as rq

def init(team_id):
    global id_score
    while len(id_score)<=team_id:
        id_score.append(dict())
    if not 'delta' in id_score[team_id].keys():
        id_score[team_id]['delta']=0
        id_score[team_id]['wins']=0
        id_score[team_id]['losses']=0


token_map = json.load(open("Token.json"))
token = token_map["Token"]
header = {"Authorization": token}

url='https://lksh-enter.ru/matches'
matches = rq.get(url, headers=header)

url='https://lksh-enter.ru/teams'
teams=rq.get(url,headers=header)

team_to_id=dict()
id_to_team=dict()
players_id=[]
players=[]

for cur in teams.json():
    id=cur['id']
    name=cur['name']
    team_to_id[name]=id
    id_to_team[id]=name
    for pl_id in cur['players']:
        players_id.append(pl_id)

#cnt=0 # удалить
for pl_id in players_id:
#    cnt+=1 #уалитьд
#    if cnt>=10:break #удалить
    url='https://lksh-enter.ru/players/'+str(pl_id)
    player=rq.get(url,headers=header)
    name=player.json()['name']+' '+player.json()['surname']
    players.append(name)

players=sorted(list(set(players)))
for player in players:
    print(player)


id_score=[]

for cur in matches.json():
    team1_score=cur['team1_score']
    team2_score=cur['team2_score']
    team1_id=cur['team1']
    team2_id=cur['team2']

    init(team1_id)
    init(team2_id)

    id_score[team1_id]['delta']+=(team1_score-team2_score)
    id_score[team2_id]['delta']+=(team2_score-team1_score)
    if team1_score>team2_score:
        id_score[team1_id]['wins']+=1
        id_score[team2_id]['losses']+=1
    elif team1_score<team2_score:
        id_score[team1_id]['losses']+=1
        id_score[team2_id]['wins']+=1

while True:
    question = input()
    if question.split()[0] == 'stats?':
        name = question.split()[1]
        if len(name)<2:
            print(0,0,0)
        name = name[1:-1]

        if not name in team_to_id.keys():
            print(0,0,0)
            continue
        team_id=team_to_id[name]
        wins=id_score[team_id]['wins']
        losses=id_score[team_id]['losses']
        delta=id_score[team_id]['delta']
        print(wins,losses,delta)

        

