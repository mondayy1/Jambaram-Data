from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
import requests
import json
import os

with open('/home/hojoong/Jambaram-Data/secrets.json') as f:
    secrets = json.loads(f.read())
key = secrets['apikey_riot']
region = 'na1'
df = pd.read_csv('/mnt/disk1/hojoong/matches/bone.csv', index_col=0)
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
}

def get_champids_from_participants(participants):
    championids = {col:0 for col in df.columns}
    for participant in participants:
        championids[str(participant['championId'])] = 1
    return championids

def list_match_ids():
    match_ids = sorted(os.listdir('/mnt/disk1/hojoong/matches/ongoing'))
    return match_ids

def save_match_infos(**kwargs):
    ti = kwargs['ti']
    match_ids = ti.xcom_pull(task_ids='list_match_ids_task')
    
    for match_id in match_ids:
        match_id = match_id[:-5]
        df = pd.read_csv('/mnt/disk1/hojoong/matches/bone.csv', index_col=0)
        url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={key}'
        response = requests.get(url)
        if response.status_code == 200:
            match_info = response.json()
            participants_blue = match_info['info']['participants'][:5]
            participants_red = match_info['info']['participants'][5:]
            championids_blue = get_champids_from_participants(participants_blue)
            championids_red = get_champids_from_participants(participants_red)
            if match_info['info']['teams'][0]['win'] == True: #Blue Win
                championids_blue['win']=1
                championids_red['win']=0
            else: #Red Win
                championids_blue['win']=0
                championids_red['win']=1
            df.loc[0] = championids_blue
            df.loc[1] = championids_red
            df.to_csv(f'/mnt/disk1/hojoong/matches/complete/{match_id}.csv', index=False)
            os.unlink(f'/mnt/disk1/hojoong/matches/ongoing/{match_id}.json')
        else: #TODOs are new matches
            break   

with DAG('riot_api_ongoing_to_complete_pipeline',
         default_args=default_args,
         schedule_interval=timedelta(minutes=30),
         tags=['riot', 'api', 'pipeline'],
         catchup=False) as dag:

    list_match_ids_task = PythonOperator(
        task_id='list_match_ids_task',
        python_callable=list_match_ids
    )

    save_match_infos_task = PythonOperator(
        task_id='save_match_infos_task',
        python_callable=save_match_infos,
        provide_context=True
    )

    list_match_ids_task >> save_match_infos_task
