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
    cursor.execute(f'SELECT * FROM today_best_comb_win')
    row = cursor.fetchall()
    if len(row) > 0:
        cursor.execute(f'DELETE FROM today_best_comb_win WHERE champions = %s', (row[0][0],))
    db.commit()

    cursor.execute(f'SELECT * FROM today_best_comb_score')
    row = cursor.fetchall()
    if len(row) > 0:
        cursor.execute(f'DELETE FROM today_best_comb_score WHERE champions = %s', (row[0][0],))
    db.commit()
    

with DAG('dailytask',
        default_args=default_args,
        schedule_interval='0 0 * * *',
        tags=['daily'],
        catchup=False) as dag:

    update_today_best_comb_task = PythonOperator(
        task_id='truncate_today_combs',
        python_callable=update_today_best_comb
    )

    update_today_best_comb_task
