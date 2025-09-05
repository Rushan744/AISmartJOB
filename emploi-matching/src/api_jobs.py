import requests
import os
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID') 
ADZUNA_API_KEY = os.getenv('ADZUNA_API_KEY')
ADZUNA_API_URL = 'https://api.adzuna.com/v1/api/jobs/fr/search/1'

def get_adzuna_jobs(what, where, results_per_page=10):
    params = {
        'app_id': ADZUNA_APP_ID,
        'app_key': ADZUNA_API_KEY,
        'what': what,
        'where': where,
        'results_per_page': results_per_page,
        'content-type': 'application/json'
    }
    response = requests.get(ADZUNA_API_URL, params=params)
    response.raise_for_status()
    return response.json()['results']

if __name__ == '__main__':
    jobs = get_adzuna_jobs(what='developer', where='Paris')
    for job in jobs:
        print(job['title'], job['company']['display_name'], job['location']['display_name'])
