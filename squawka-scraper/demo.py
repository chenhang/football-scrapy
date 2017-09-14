import pandas as pd
import requests
from squawka.utils import SquawkaReport


def re_download_data():
    f = open('./errors.txt')
    files = []
    for line in f:
        file_path = line
        league = line.split('/')[-1].split('_')[0]
        game_id = line.split('.')[0].split('_')[-1]
        url = 'http://s3-irl-' + league + '.squawka.com/dp/ingame/' + game_id
        response = requests.get(url)
        with open(file_path, 'wb') as file:
            file.write(response.content)
        report = SquawkaReport(file_path)
        goals_attempts = pd.DataFrame(report.goals_attempts)
        print report.kickoff
        goals_attempts[goals_attempts['type'] == 'goal']

    f.close()


report = SquawkaReport('data/epl_28904.xml')
goals_attempts = pd.DataFrame(report.action_areas)
# goals_attempts = pd.DataFrame(report.goals_attempts)
print goals_attempts
