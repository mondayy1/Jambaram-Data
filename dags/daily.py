from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
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

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
}

def update_today_best_comb():
    tables = ['today_best_comb_win', 'today_best_comb_score']

    for table in tables:
        cursor.execute(f'TRUNCATE TABLE {table}')
        db.commit()

with DAG('daily',
        default_args=default_args,
        schedule_interval='0 9 * * *',
        tags=['daily'],
        catchup=False) as dag:

    update_today_best_comb_task = PythonOperator(
        task_id='fetch_featured_games_task',
        python_callable=update_today_best_comb
    )

    update_today_best_comb_task
