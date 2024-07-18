from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import pandas as pd
import requests
import psycopg2
import json
import os

with open('/home/hojoong/Jambaram-Data/secrets.json') as f:
    secrets = json.loads(f.read())
key = secrets['apikey_riot']

db = psycopg2.connect(host=secrets['DB']['host'],
                      dbname=secrets['DB']['dbname'],
                      user=secrets['DB']['user'],
                      password=secrets['DB']['password'],
                      port=secrets['DB']['port'])
cursor = db.cursor()

df = pd.read_csv('/mnt/disk1/hojoong/matches/bone.csv')
columns = ', '.join([f'"{key}"' for key in df.columns])
placeholders = ', '.join(['%s' for _ in range(len(df.columns))])
insert_query = '''
INSERT INTO match_data_champion_168 ({})
VALUES ({});
'''
region = 'na1'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
}

def get_champids_from_participants(participants):
    championids = {col:'0' for col in df.columns}
    dpm = 0; gpm = 0; ehs = 0
    for participant in participants:
        championids[str(participant['championId'])] = '1'
        dpm += participant['challenges']['damagePerMinute'] / 2 / 100
        gpm += participant['challenges']['goldPerMinute'] / 100
        ehs += participant['challenges']['effectiveHealAndShielding'] / 2000
    score = dpm * 1.1 + gpm * 0.9 + ehs * 0.5
    return score, championids

def list_match_ids():
    #match_ids = sorted(os.listdir('/mnt/disk1/hojoong/matches/ongoing'))
    cursor.execute('SELECT * FROM match_ids_ongoing;')
    matches = cursor.fetchall()
    return matches

def save_match_infos(**kwargs):
    ti = kwargs['ti']
    matches = ti.xcom_pull(task_ids='list_match_ids_task')
    
    for match_id, date in matches:
        df = pd.read_csv('/mnt/disk1/hojoong/matches/bone.csv')
        url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={key}'
        response = requests.get(url)
        if response.status_code == 200:
            match_info = response.json()

            participants_blue = match_info['info']['participants'][:5]
            participants_red = match_info['info']['participants'][5:]

            score_blue, championids_blue = get_champids_from_participants(participants_blue)
            score_red, championids_red = get_champids_from_participants(participants_red)

            if match_info['info']['teams'][0]['win'] == True: #Blue Win
                championids_blue['win']='1'
                championids_red['win']='0'
            else: #Red Win
                championids_blue['win']='0'
                championids_red['win']='1'
            
            championids_blue['score'] = score_blue
            championids_red['score'] = score_red

            cursor.execute(insert_query.format(columns, placeholders), list(championids_blue.values()))
            cursor.execute(insert_query.format(columns, placeholders), list(championids_red.values()))

            cursor.execute('DELETE FROM match_ids_ongoing WHERE id = %s;', (match_id, ))

            db.commit()
        else: #MATCH ON GOING, DOESNT HAVE TO CHECK
            pass

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
