import requests
from fake_headers import Headers
import logging
import csv
import logging
import asyncio
import json

# Initialization logger
logger = logging.basicConfig(filename="HHParser.log", level=logging.DEBUG)
# Variables for parsing
BASE_API_URL = "https://api.hh.ru/"
MY_HEADERS = Headers(os="win",headers=False).generate() # Headers for parsing


def get_vacancies(in_data):
    # in_data - PYTHON array which consists of:
    # profession - type 'str'
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
        for i in range(len(out_data['items'])):
            if out_data['items'][i]['salary'] == None:
                out_data['items'][i]['salary'] = dict()
                out_data['items'][i]['salary']['from'] = 'Не указана'
                out_data['items'][i]['salary']['to'] = 'Не указана'
            elif out_data['items'][i]['salary']['from'] == None:
                out_data['items'][i]['salary']['from'] = 'Не указано'
            elif out_data['items'][i]['salary']['to'] == None:
                out_data['items'][i]['salary']['to'] = 'Не указано'
        return out_data
    else:
        out_data['status'] = req.status_code
        out_data['items'] = dict()
        return out_data
