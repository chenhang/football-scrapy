# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import os
import time
import json
import csv
import re
from math import *
from datetime import datetime
from bs4 import BeautifulSoup

BASE_URL = 'https://www.whoscored.com'
STATS_KEYS = [u'team', u'name', u'position', u'playMins', u'result', u'goals', u'assists', u'goalsConceded', u'penaltyConceded', 
                u'cornersTotal', u'aerialsWon', u'dribblesLost', u'shotsTotal', u'passesAccurate', u'tackleUnsuccesful', 
                u'defensiveAerials', u'aerialsTotal', u'offensiveAerials', u'passesTotal', u'throwInsTotal', 
                u'offsidesCaught', u'interceptions', u'ratings', u'touches', u'dispossessed', u'parriedSafe', u'claimsHigh', 
                u'clearances', u'throwInAccuracy', u'collected', u'parriedDanger', u'possession', u'shotsOffTarget', u'dribblesAttempted', 
                u'shotsOnPost', u'dribblesWon', u'cornersAccurate', u'tackleSuccess', u'throwInsAccurate', u'dribbleSuccess', u'errors', 
                u'aerialSuccess', u'shotsBlocked', u'tacklesTotal', u'tackleSuccessful', u'shotsOnTarget', u'dribbledPast', 
                u'passesKey', u'foulsCommited', u'totalSaves', u'passSuccess']

RATING_KEYS = ['team', 'name', 'position', 'adjustedRating', 'overallRating', 'parriedDangerRating', 'cccPassesRating', 'shotsAccuracyRating', 
                'errorsRating', 'goalsConcededRating', 'dribbleSuccessRating', 'aerialSuccessRating', 'collectedRating', 
                'totalSavesRating', 'dribbledPastRating', 'goalsRating', 'defenseThreeRatting', 'passesAccuracyRating']

RATING_CONFIG = {
    
}
def load_json(file_name):
    with open(file_name) as json_data:
        d = json.load(json_data)
        return d


def write_json(file_name, json_data):
    with open(file_name, 'w') as outfile:
        json.dump(json_data, outfile)
        return json_data


# script = soup.find('script', text=re.compile('calendarParameter'))
# json_text = re.search(r'calendarParameter\),\s+(\[\[(.|\n)*\])',
#                       script.string, flags=re.DOTALL | re.MULTILINE).group(1).replace("'", '"').rstrip('\r\n')
def get_fixtures(driver, league_url, only_now=True):
    driver.get(league_url)
    html = driver.page_source
    fixture_url = driver.find_elements_by_xpath(
        '//*[@id="sub-navigation"]/ul/li[2]/a')[0].get_attribute('href')
    driver.get(fixture_url)
    print(fixture_url)
    fixtures = {}
    total = len(fixtures)
    season = '-'.join(fixture_url.split('-')[-2:])
    while True:
        html = driver.page_source
        soup = BeautifulSoup(html)
        table = soup.find('table', id='tournament-fixture')
        trs = table.find_all('tr')
        date = None
        for tr in trs:
            print(tr.text)
            if 'rowgroupheader' in tr.get('class'):
                date = str(datetime.strptime(tr.text.split(', ')[-1], '%b %d %Y').date())
            else:
                id = tr.attrs['data-id']
                print(id)
                if fixtures.has_key(id) and fixtures[id].get('status', 0) == 'FT':
                    continue
                status = tr.find('td', class_='status').text
                time_str = tr.find('td', class_='time').text
                home = tr.find('td', class_='home').text
                home_url = tr.find('td', class_='home').find('a').get('href')
                away = tr.find('td', class_='away').text
                away_url = tr.find('td', class_='away').find('a').get('href')
                url = tr.find('td', class_='result').find('a').get('href')
                result = tr.find('td', class_='result').text
                fixtures[id] = {'status': status, 'time': time_str, 'date': date, 'season': season, 
                                'home': home, 'home_url': home_url, 'away': away, 
                                'away_url': away_url, 'result': result, 'url': url, 'id': id}
        if len(fixtures) == total:
            break
        total = len(fixtures)
        time.sleep(3)
        print('Current Counts:', total)
        elements = driver.find_elements_by_xpath(
            '//*[@id="date-controller"]/a[1]')
        if len(elements) == 0:
            break
        prev = driver.find_elements_by_xpath(
            '//*[@id="date-controller"]/a[1]')[0]
        ajax_click(driver, prev)
    path = os.path.join('matches', 
        league_url.split('/')[-1], season)
    if not os.path.exists(path):
        os.makedirs(path)
    write_json(path + '/fixtures.json', fixtures)


def parse_match(html):
    soup = BeautifulSoup(html)
    script = soup.find('script', text=re.compile('matchCentreData'))
    json_text = re.search(r'matchCentreData\s+=\s+(\{.*?\});\n',
                          script.string, flags=re.DOTALL | re.MULTILINE).group(1)
    data = json.loads(json_text)
    return data


def parse_stats(file_name):
    # keys:
    # [u'startDate', u'periodCode', u'home', u'attendance', u'expandedMinutes',
    # u'away', u'timeStamp', u'score', u'etScore', u'commonEvents', u'events', u'referee',
    # u'maxMinute', u'elapsed', u'pkScore', u'startTime', u'weatherCode',
    # u'expandedMaxMinute', u'periodMinuteLimits', u'timeoutInSeconds', u'periodEndMinutes',
    # u'htScore', u'playerIdNameDictionary', u'maxPeriod', u'minuteExpanded', u'venueName',
    # u'statusCode', u'ftScore']
    data = load_json(file_name)
    stats = []
    penaltyConceded = {}
    assists = {}
    team_fields = ['home', 'away']
    goals = {}
    goals_mins = {'home': [], 'away': []}
    
    for event in data['events']:
        # penaltyConceded: 133
        if 133 in event.get(u'satisfiedEventsTypes', []):
            penaltyConceded[event[u'playerId']] = penaltyConceded.get(event['playerId'], 0) + 1
        # assist: 91
        if 91 in event.get(u'satisfiedEventsTypes', []):
            assists[event[u'playerId']] = assists.get(event['playerId'], 0) + 1
    for team in team_fields:
        # keys:
        # [u'averageAge', u'stats', u'name', u'incidentEvents', u'players', u'formations',
        # u'countryName', u'field', u'teamId', u'scores', u'shotZones', u'managerName']
        for event in data[team].get('incidentEvents', []):
            if event.has_key('isGoal'):
                goals[event[u'playerId']] = goals.get(event['playerId'], 0) + 1
                goals_mins[team].append(int(event['expandedMinute']))
    for team in team_fields:
        other_team = team_fields[1 - team_fields.index(team)]
        for player in data[team]['players']:
            # keys:
            # [u'shirtNo', u'stats', u'name', u'weight', u'playerId', u'age',
            # u'height', u'isManOfTheMatch', u'field', u'isFirstEleven', u'position']
            # stats keys:
            # [u'cornersTotal', u'aerialsWon', u'dribblesLost', u'shotsTotal', u'passesAccurate',
            # u'tackleUnsuccesful', u'defensiveAerials', u'aerialsTotal', u'offensiveAerials',
            # u'passesTotal', u'throwInsTotal', u'dispossessed', u'interceptions', u'ratings',
            # u'touches', u'offsidesCaught', u'parriedSafe', u'clearances', u'throwInAccuracy',
            # u'collected', u'parriedDanger', u'possession', u'shotsOffTarget', u'dribblesAttempted',
            # u'dribblesWon', u'cornersAccurate', u'tackleSuccess', u'throwInsAccurate', u'dribbleSuccess',
            # u'errors', u'aerialSuccess', u'tacklesTotal', u'tackleSuccessful', u'shotsOnTarget',
            # u'passesKey', u'dribbledPast', u'foulsCommited', u'shotsBlocked', u'totalSaves', u'passSuccess']
            player_stats = {u'name': player['name'],
                            u'position': player['position'], u'team': data[team]['name']}
            for key, values in player['stats'].iteritems():
                if key is not u'ratings':
                    player_stats[key] = sum(values.values())
            player_stats['goals'] = goals.get(player['playerId'], 0)
            player_stats['penaltyConceded'] = penaltyConceded.get(player['playerId'], 0)
            player_stats['assists'] = assists.get(player['playerId'], 0)
            if player.has_key(u'isFirstEleven'):
                player_stats['playMins'] = player.get('subbedOutExpandedMinute', 90)
                player_stats['goalsConceded'] = sum(x <= player.get('subbedOutExpandedMinute', data['expandedMaxMinute']) for x in goals_mins[other_team])
            else:
                player_stats['playMins'] = abs(data['expandedMaxMinute'] - player.get('subbedInExpandedMinute', data['expandedMaxMinute']))
                player_stats['goalsConceded'] = sum(x >= player.get('subbedInExpandedMinute', data['expandedMaxMinute']) for x in goals_mins[other_team])
            stats.append(player_stats)
    with open(file_name.replace('.json', '.csv'), 'wb') as output_file:
        dict_writer = csv.DictWriter(
            output_file, fieldnames=STATS_KEYS, restval=0)
        dict_writer.writeheader()
        dict_writer.writerows(stats)

def safe_division(a, b):
    if b == 0:
        return 0
    else:
        return a / b

def erfcc(x):
    """Complementary error function."""
    z = abs(x)
    t = 1. / (1. + 0.5*z)
    r = t * exp(-z*z-1.26551223+t*(1.00002368+t*(.37409196+
        t*(.09678418+t*(-.18628806+t*(.27886807+
        t*(-1.13520398+t*(1.48851587+t*(-.82215223+
        t*.17087277)))))))))
    if (x >= 0.):
        return r
    else:
        return 2. - r

def normcdf(x, mu, sigma):
    t = x - mu
    y = 0.5 * erfcc(-t / (sigma * sqrt(2.0)))
    if y > 1.0:
        y = 1.0
    return y


def normpdf(x, mu, sigma):
    u = (x - mu) / abs(sigma)
    y = (1 / (sqrt(2 * pi) * abs(sigma))) * exp(-u * u / 2)
    return y


def normdist(x, mu, sigma, f):
    if f:
        y = normcdf(x, mu, sigma)
    else:
        y = normpdf(x, mu, sigma)
    return y


def calculate_scores(file_name):
    # stats keys:
    # [u'cornersTotal', u'aerialsWon', u'dribblesLost', u'shotsTotal', u'passesAccurate',
    # u'tackleUnsuccesful', u'defensiveAerials', u'aerialsTotal', u'offensiveAerials',
    # u'passesTotal', u'throwInsTotal', u'dispossessed', u'interceptions', u'ratings',
    # u'touches', u'offsidesCaught', u'parriedSafe', u'clearances', u'throwInAccuracy',
    # u'collected', u'parriedDanger', u'possession', u'shotsOffTarget', u'dribblesAttempted',
    # u'dribblesWon', u'cornersAccurate', u'tackleSuccess', u'throwInsAccurate', u'dribbleSuccess',
    # u'errors', u'aerialSuccess', u'tacklesTotal', u'tackleSuccessful', u'shotsOnTarget',
    # u'passesKey', u'dribbledPast', u'foulsCommited', u'shotsBlocked', u'totalSaves', u'passSuccess']
    results = []
    with open(file_name, "rb") as theFile:
        reader = csv.DictReader(theFile)
        keys = []
        for line in reader:
            team, name, position = line['team'], line['name'], line['position']
            result = {}
            if float(line['playMins']) > 0:
                defenseThree = float(line['interceptions']) + float(line['tackleSuccessful']) + float(line['clearances'])
                aerialSuccess = safe_division(float(line['aerialsWon']), float(line['aerialsTotal']))
                shotsAccuracy = safe_division(float(line['shotsOnTarget']), float(line['shotsTotal']))
                passesAccuracy = safe_division(float(line['passesAccurate']), float(line['passesTotal']))
                errors = float(line['errors']) + float(line['penaltyConceded']) + float(line['dispossessed'])
                cccPasses = float(line['passesKey']) + float(line['assists'])
                if position in ['FW', 'FWL', 'FWR']:
                    result['shotsAccuracyRating'] = normdist(shotsAccuracy, 0.33, 0.21, True) * 0.2 * 100
                    result['aerialSuccessRating'] = normdist(aerialSuccess, 0.33, 0.21, True) * 0.1 * 100
                    result['dribbleSuccessRating'] = normdist(float(line['dribbleSuccess']), 1, 1.42, True) * 0.05 * 100
                    result['passesAccuracyRating'] = normdist(passesAccuracy, 0.7, 0.13, True) * 0.2 * 100
                    result['defenseThreeRatting'] = normdist((defenseThree) * 90 / float(line['playMins']), 1.1, 0.7, True) * 0.05 * 100
                    result['cccPassesRating'] = float(line['passesKey']) * 6.0 * 90 / float(line['playMins'])# * 0.2
                    result['goalsRating'] = float(line['goals']) * 17.0 * 90 / float(line['playMins'])# * 0.2
                elif position in ['AMC', 'SS', 'AML', 'AMR']:
                    result['shotsAccuracyRating'] = normdist(shotsAccuracy, 0.3, 0.09, True) * 0.05 * 100
                    result['aerialSuccessRating'] = normdist(aerialSuccess, 0.3, 0.09, True) * 0.05 * 100
                    result['dribbleSuccessRating'] = normdist(float(line['dribbleSuccess']), 2, 1.42, True) * 0.15 * 100
                    result['passesAccuracyRating'] = normdist(passesAccuracy, 0.8, 0.12, True) * 0.2 * 100
                    result['defenseThreeRatting'] = normdist((defenseThree) * 90 / float(line['playMins']), 1.5, 0.43, True) * 0.1 * 100
                    result['cccPassesRating'] = float(line['passesKey']) * 5 * 90 / float(line['playMins'])# * 0.3
                    result['goalsRating'] = float(line['goals']) * 25 * 90 / float(line['playMins'])# * 0.2
                elif position in ['WF', 'IF']:
                    result['shotsAccuracyRating'] = normdist(shotsAccuracy, 0.33, 0.15, True) * 0.05 * 100
                    result['aerialSuccessRating'] = normdist(aerialSuccess, 0.3, 0.09, True) * 0.05 * 100
                    result['dribbleSuccessRating'] = normdist(float(line['dribbleSuccess']), 2, 1.42, True) * 0.15 * 100
                    result['passesAccuracyRating'] = normdist(passesAccuracy, 0.75, 0.08, True) * 0.15 * 100
                    result['defenseThreeRatting'] = normdist((defenseThree) * 90 / float(line['playMins']), 1.5, 0.75, True) * 0.1 * 100
                    result['cccPassesRating'] = float(line['passesKey']) * 6.25 * 90 / float(line['playMins'])# * 0.35
                    result['goalsRating'] = float(line['goals']) * 20 * 90 / float(line['playMins'])# * 0.15
                    result['errorsRating'] = 0.05 * 100 - errors * 25 / 90 * float(line['playMins']) 
                elif position in ['CM', 'LCM', 'RCM', 'MC', 'ML', 'MR']:
                    result['aerialSuccessRating'] = normdist(aerialSuccess, 0.5, 0.21, True) * 0.05 * 100
                    result['dribbleSuccessRating'] = normdist(float(line['dribbleSuccess']), 3, 1.5, True) * 0.1 * 100
                    result['passesAccuracyRating'] = normdist(passesAccuracy, 0.83, 0.08, True) * 0.2 * 100
                    result['defenseThreeRatting'] = normdist((defenseThree) * 90 / float(line['playMins']), 3, 2.29, True) * 0.25 * 100
                    result['cccPassesRating'] = float(line['passesKey']) * 5 * 90 / float(line['playMins'])# * 0.25
                    result['goalsRating'] = float(line['goals']) * 20 * 90 / float(line['playMins'])# * 0.1
                    result['errorsRating'] = 0.1 * 100 - errors * 15 / 90 * float(line['playMins']) 
                    result['dribbledPastRating'] = 0.05 * 100 - float(line['dribbledPast']) * 5 * 90 / float(line['playMins'])
                elif position in ['DM', 'DMC']:
                    result['aerialSuccessRating'] = normdist(aerialSuccess, 0.4, 0.21, True) * 0.1 * 100
                    result['passesAccuracyRating'] = normdist(passesAccuracy, 0.85, 0.08, True) * 0.2 * 100
                    result['defenseThreeRatting'] = normdist((defenseThree) * 90 / float(line['playMins']), 6.5, 3.6, True) * 0.3 * 100
                    result['cccPassesRating'] = float(line['passesKey']) * 5 * 90 / float(line['playMins'])# * 0.1
                    result['goalsRating'] = float(line['goals']) * 25 * 90 / float(line['playMins'])# * 0.05
                    result['errorsRating'] = 0.15 * 100 - errors * 25 / 90 * float(line['playMins'])
                    result['dribbledPastRating'] = 0.1 * 100 - (float(line['dribbledPast']) * 4 * 90 / float(line['playMins']))
                elif position in ['DL', 'DR']:
                    result['aerialSuccessRating'] = normdist(aerialSuccess, 0.5, 0.21, True) * 0.05 * 100
                    result['dribbleSuccessRating'] = normdist(float(line['dribbleSuccess']), 1, 0.7, True) * 0.15 * 100
                    result['passesAccuracyRating'] = normdist(passesAccuracy, 0.75, 0.08, True) * 0.1 * 100
                    result['defenseThreeRatting'] = normdist((defenseThree) * 90 / float(line['playMins']), 8, 3.6, True) * 0.3 * 100
                    result['cccPassesRating'] = float(line['passesKey']) * 5 * 90 / float(line['playMins'])# * 0.1
                    result['goalsRating'] = float(line['goals']) * 25 * 90 / float(line['playMins'])# * 0.05
                    result['errorsRating'] = 0.09 * 100 - errors * 15 * 90 / float(line['playMins'])
                    result['dribbledPastRating'] = 0.16 * 100 - (float(line['dribbledPast']) * 8 * 90 / float(line['playMins']))
                elif position in ['DC']:
                    result['aerialSuccessRating'] = normdist(aerialSuccess, 0.5, 0.21, True) * 0.25 * 100
                    result['passesAccuracyRating'] = normdist(passesAccuracy, 0.8, 0.08, True) * 0.1 * 100
                    result['defenseThreeRatting'] = normdist((defenseThree) * 90 / float(line['playMins']), 10, 7, True) * 0.3 * 100
                    result['cccPassesRating'] = float(line['passesKey'])  * 5 * 90 / float(line['playMins'])# * 0.05
                    result['goalsRating'] = float(line['goals']) * 15 * 90 / float(line['playMins'])# * 0.05
                    result['errorsRating'] = 0.15 * 100 - errors * 30 * 90 / float(line['playMins'])
                    result['dribbledPastRating'] = 0.1 * 100 - (float(line['dribbledPast']) * 8 * 90 / float(line['playMins']))
                elif position in ['GK']:
                    result['passesAccuracyRating'] = normdist(passesAccuracy, 0.67, 0.22, True) * 0.1 * 100
                    result['totalSavesRating'] = normdist(safe_division(float(line['totalSaves']), float(line['playMins'])) * 90, 3, 1.29, True) * 0.25 * 100
                    result['collectedRating'] = normdist(safe_division(float(line['collected']) + float(line['claimsHigh']), float(line['playMins'])) * 90, 1, 1.29, True) * 0.15 * 100
                    result['parriedDangerRating'] = normdist(safe_division(float(line['parriedDanger']), float(line['playMins'])) * 90, 0.1, 0.3, True) * 0.15 * 100
                    result['goalsConcededRating'] = 0.2 * 100 - (float(line['goalsConceded']) * 10 * 90 / float(line['playMins']))
                    result['errorsRating'] = 0.15 * 100 - errors * 25 * 90 / float(line['playMins'])
            result['overallRating'] = sum(result.values())/10 + 0
            result['adjustedRating'] = result['overallRating'] * 0.4
            result.update({'team': team, 'name': name, 'position': position})
            results.append(result)
            with open(file_name.replace('match.csv', 'rating.csv'), 'wb') as output_file:
                dict_writer = csv.DictWriter(
                    output_file, fieldnames=RATING_KEYS, restval=0)
                dict_writer.writeheader()
                dict_writer.writerows(results)

# Url sample
# https://www.whoscored.com/Matches/1190270/Live/England-Premier-League-2017-2018-Liverpool-Manchester-United
def get_match(driver, url):
    driver.get(url)
    print(url)
    time.sleep(3)
    print('Load HTML Done')
    season = re.search(r"2[0-9]{3}-2[0-9]{3}",url).group(0)
    league = url.split('/')[-1].split(season)[0][:-1]
    html = driver.page_source
    data = parse_match(html)
    print('Load JSON From HTML')
    date = data['startDate'].split('T')[0]
    home = data['home']['name']
    away = data['away']['name']
    path = os.path.join('matches', league, season, date, '-'.join([home, away]))
    if not os.path.exists(path):
        os.makedirs(path)
    
    with open(path + '/match.html', 'w') as file:
        file.write(html)
    write_json(path + '/match.json', data)
    parse_stats(path + '/match.json')
    calculate_scores(path + '/match.csv')
    print('All Done')


def element_visiable(driver, class_name):
    len([
        e for e in driver.find_elements_by_class_name(class_name)
        if e.value_of_css_property('display') != 'none'
    ]) > 0


def ajax_complete(driver):
    try:
        return 0 == driver.execute_script(
            "return jQuery.active"
        )  # and ((not element_visiable(driver, 'loading-wrapper')) or element_visiable(driver, 'statistics-table-tab'))
    except WebDriverException:
        pass


def ajax_click(driver, element):
    driver.execute_script("arguments[0].click();", element)

    WebDriverWait(driver, 10000).until(ajax_complete,
                                       "Timeout waiting for page to load")
    time.sleep(1)

BASE_URL = "https://www.whoscored.com"
pl_url = "https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League"
ia_url = "https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A"
league_urls = [
    "https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League",
    "https://www.whoscored.com/Regions/81/Tournaments/3/Germany-Bundesliga",
    "https://www.whoscored.com/Regions/108/Tournaments/5/Italy-Serie-A",
    "https://www.whoscored.com/Regions/206/Tournaments/4/Spain-La-Liga",
    "https://www.whoscored.com/Regions/74/Tournaments/22/France-Ligue-1",
    "https://www.whoscored.com/Regions/250/Tournaments/12/Europe-UEFA-Champions-League",
    "https://www.whoscored.com/Regions/250/Tournaments/30/Europe-UEFA-Europa-League",
    "https://www.whoscored.com/Regions/177/Tournaments/21/Portugal-Liga-NOS",
    "https://www.whoscored.com/Regions/155/Tournaments/13/Seasons/6826/Netherlands-Eredivisie",
]

def get_all_fixtures(driver, league_urls):
    for league_url in league_urls:
        get_fixtures(driver, league_url)
def get_all_matches(driver):
    for dir_name in os.listdir('matches'):
        league_path = os.path.join('matches', dir_name)
        if os.path.isdir(league_path):
            for season in os.listdir(league_path):
                season_path = os.path.join(league_path, season)
                if os.path.isdir(season_path):
                    print season_path
                    fixtures = load_json(os.path.join(season_path, 'fixtures.json'))
                    log_path = os.path.join(season_path, 'log.json')
                    logs = []
                    if os.path.exists(log_path):
                        logs = load_json(log_path)
                    for id, match in fixtures.iteritems():
                        url = BASE_URL+match['url']
                        if id not in logs and match.get('stats', 0) == 'FT' or match.get('status', 0) == 'FT':
                            print(url, 'Start')
                            start_time = time.time()
                            get_match(driver, url)
                            time.sleep(5)
                            print("Match cost: --- %s seconds ---" % (time.time() - start_time))
                            print(url, 'Done')
                            logs.append(id)
                            write_json(log_path, logs)
                         


options = webdriver.ChromeOptions()
# options.add_argument('headless')
# options.add_argument('window-size=1200x600')
driver = webdriver.Chrome(executable_path="chromedriver", chrome_options=options)
driver.implicitly_wait(100)
get_all_matches(driver)
driver.quit()