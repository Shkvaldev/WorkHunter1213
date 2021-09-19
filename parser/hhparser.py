import requests
from fake_headers import Headers
<<<<<<< HEAD
import logging
=======
import csv
import logging
import asyncio
>>>>>>> 0895e9caea730afdbbbf1f0450f5f7bb17f0a6d3
import json

# Initialization logger
logger = logging.basicConfig(filename="HHParser.log", level=logging.DEBUG)
# Initialization variables for parsing
BASE_API_URL = "https://api.hh.ru/"
<<<<<<< HEAD
MY_HEADERS = Headers(os="win",headers=False).generate() # Headers for parsing
# HH api defintions
EXPERIENCE_RU_DICT = {'0': 'Нет опыта', '1': 'От 1 до 3 лет', '2': 'От 3 до 6 лет', '3': 'Более 6 лет'}
#EXPERIENCE_EN_DICT = {'0': 'Without experience', '1': '{'Accept': '*/*', 'Connection': 'keep-alive', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.109 Safari/537.36 OPR/51.0.2830.34'}Between 1 and 3', '2': 'Between 3 and 6', '3': 'More than 6'}
AREA_DICT = {'RU': 113, 'UK': 5}
=======
MY_HEADERS = Headers(os="win",headers=False) # Headers for parsing

# HH api defintions

>>>>>>> 0895e9caea730afdbbbf1f0450f5f7bb17f0a6d3

def get_vacancies(in_data):
    # in_data - PYTHON array which consists of:
    # profession - type 'str'
<<<<<<< HEAD
    # experience - type 'int'
    # area - type 'str'
    # currency - type 'str'
    # salary - type 'int'
    out_data = dict()
    params = {
        'text': in_data['profession'],
        'experience': in_data['experience'],
        'area': in_data['area'],
        'currency': in_data['currency'],
        'salary': in_data['salary'],
        'per_page': 10
    }
    req = requests.get(url=BASE_API_URL+'vacancies', params=params, headers=MY_HEADERS)
    if req.status_code == 200:
        first_answer = json.loads(req.text)
        out_data['status'] = req.status_code 
        out_data['source'] = 'hh.ru'
        out_data['pages'] = first_answer['pages']
        out_data['items'] = dict()
        for key in range(len(first_answer['items'])):
            out_data['items'][key] = first_answer['items'][key]
        return out_data
    else:
        out_data['status'] = req.status_code
        return out_data
=======
    # 
    pass
>>>>>>> 0895e9caea730afdbbbf1f0450f5f7bb17f0a6d3
