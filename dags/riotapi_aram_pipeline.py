from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
import requests
import psycopg2
import json

with open('/home/hojoong/Jambaram-Data/secrets.json') as f:
    secrets = json.loads(f.read())

db = psycopg2.connect(host=secrets['DB']['host'],
                      dbname=secrets['DB']['dbname'],
                      user=secrets['DB']['user'],
                      password=secrets['DB']['password'],
                      port=secrets['DB']['port'])
cursor = db.cursor()

key = secrets['apikey_riot']
region = 'na1'
match_region = 'NA1_'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
}

def fetch_featured_games():
    url = f'https://{region}.api.riotgames.com/lol/spectator/v5/featured-games?api_key={key}'
    response = requests.get(url)
    if response.status_code == 200:
        featured_games = response.json()
        return featured_games
    else:
        raise Exception(f"Failed to fetch featured games. Status code: {response.status_code}")

def filter_aram_games(**kwargs):
    ti = kwargs['ti']
    featured_games = ti.xcom_pull(task_ids='fetch_featured_games_task')
    aram_games = [game for game in featured_games['gameList'] if 'ARAM' in game['gameMode']]
    return aram_games

def save_match_ids_to_json(**kwargs):
    ti = kwargs['ti']
    aram_games = ti.xcom_pull(task_ids='filter_aram_games_task')
    date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for game in aram_games:
        match_id = match_region + str(game['gameId'])
        #with open(f'/mnt/disk1/hojoong/matches/ongoing/NA1_{match_id}.json', 'w') as f:
        #    json.dump(game, f, indent=2)
        #f.close()
        cursor.execute(
            "INSERT INTO match_ids_ongoing (id, date) VALUES (%s, %s)",
            (match_id, date)
        )
    db.commit()

with DAG('riot_api_data_pipeline',
         default_args=default_args,
         schedule_interval=timedelta(minutes=1),
         tags=['riot', 'api', 'pipeline'],
         catchup=False) as dag:

    fetch_featured_games_task = PythonOperator(
        task_id='fetch_featured_games_task',
        python_callable=fetch_featured_games
    )

    filter_aram_games_task = PythonOperator(
        task_id='filter_aram_games_task',
        python_callable=filter_aram_games,
        provide_context=True
    )

    save_match_ids_task = PythonOperator(
        task_id='save_match_ids_task',
        python_callable=save_match_ids_to_json,
        provide_context=True
    )

    fetch_featured_games_task >> filter_aram_games_task >> save_match_ids_task
