import json
import requests as rq
from datetime import datetime

def init(team_id,id_score):
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
