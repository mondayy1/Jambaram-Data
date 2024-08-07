![python](https://img.shields.io/badge/python-3.10.14-blue.svg?style=flat-square)
![miniforge](https://img.shields.io/badge/miniforge-24.5.0-blue.svg?style=flat-square)

# :sparkles: Jambaram-Data
> ARAM(칼바람) champion combination recommendation system [Demo](http://jambaram.xyz)

#### Architecture
![structure](https://github.com/user-attachments/assets/cf7b2434-18fc-43e8-9b6b-ec621ba4e5b1)


# :camel: Data architecture
#### DB Diagram
<img width="527" alt="Screenshot 2024-07-24 at 12 59 32 AM" src="https://github.com/user-attachments/assets/a4dee1da-e7d3-446a-a519-dedb07a4346b">

#### Pipeline
![pipeline](https://github.com/user-attachments/assets/5b9dbce9-33a7-431d-a576-66b65389d4c0)


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

패키지 설치
```
$ pip install -r requirements.txt
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

