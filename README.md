# Jambaram-Data
ARAM(칼바람) champion combination recommendation system

아키텍쳐 사진

# Data Pipeline

사진: db table

# :floppy_disk: Installation
가상환경 생성
```
$ conda create -n venv-name python=3.10
```

가상환경 실행
```
$ conda activate venv-name
```

Airflow 설치
```
$ pip install apache-airflow
```

폴더 이동 (default=airflow)
```
$ cd airflow
```


Git Clone
```
$ git clone git@github.com:mondayy1/Jambaram-Data.git
```

DB 초기화, sqlite가 기본
```
$ airflow db init
```

Airflow 유저 생성
```
$ airflow users create --username {Login_ID} --firstname {First_NAME} --lastname {Last_NAME} --role Admin --password {Password} --email {Email}
```

Airflow 웹서버 실행 (기본포트 8080)
```
$ airflow webserver
```

Airflow 스케쥴러 실행
```
$ airflow scheduler
```

localhost:8080 접속!

