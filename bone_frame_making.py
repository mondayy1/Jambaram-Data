import pandas as pd
import requests
import json

ddragonurl = 'https://ddragon.leagueoflegends.com/cdn/14.14.1/data/en_US/champion.json'
response = requests.get(ddragonurl)
data = response.json()

champion_dict = {}
champions = list(data['data'].keys())
for champion in champions:
    champion_dict[int(data['data'][champion]['key'])] = data['data'][champion]['name']

champion_dict = dict(sorted(champion_dict.items()))

for id, name in champion_dict.items():
    print(id, name)

champion_dict['win'] = 0
champion_dict['score'] = 0

df = pd.DataFrame(columns=list(champion_dict.keys()))

df.to_csv('/mnt/disk1/hojoong/matches/bone.csv', index=False)