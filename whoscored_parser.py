# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import os
import time
import json
from bs4 import BeautifulSoup

OFFICAL_TOURMENTS = [
    u'Ta\xe7a de Portugal', 'Bundesliga', 'La Liga', 'Dutch Super Cup',
    u'Troph\xe9e des Champions', 'Coupe de France', 'Peace Cup',
    'Coupe de la Ligue', 'Copa del Rey', 'Community Shield', 'Serie A',
    'Supercopa de Espana', 'Supercoppa Italiana', 'FIFA Club World Cup',
    'Super Cup', 'Carlsberg Cup', 'German Super Cup', 'Liga NOS', 'DFB Pokal',
    'League Cup', 'Ligue 1', 'UEFA Champions League', 'UEFA Europa League',
    'Coppa Italia', 'UEFA Super Cup', 'FA Cup', 'Playoff',
    'Promotion/Relegation Playoff', 'Eredivisie', 'Premier League', 'KNVB Cup'
]


def get_data_list():
    leagues = {}
    for league_file_name in os.listdir('teams'):
        league_path = os.path.join('teams', league_file_name)
        if os.path.isdir(league_path):
            league_attributes = league_file_name.split('-')
            nation = league_attributes[0]
            league_id = league_attributes[-1]
            league_name = ' '.join(league_attributes[1:-1])
            league_info = {
                'id': league_id,
                'name': league_name,
                'path': league_path,
                'teams': {}
            }
            for team_file_name in os.listdir(league_path):
                team_path = os.path.join(league_path, team_file_name)
                if os.path.isdir(team_path):
                    team_attributes = team_file_name.split('-')
                    nation = team_attributes[0]
                    team_id = team_attributes[-1]
                    team_name = ' '.join(team_attributes[1:-1])
                    team_info = {
                        'id': team_id,
                        'name': team_name,
                        'path': team_path,
                        'tourments': {},
                        'overall': {}
                    }
                    overall_path = os.path.join(team_path, 'Overall')
                    for overall_file_name in os.listdir(overall_path):
                        if overall_file_name.endswith('.html'):
                            team_info['overall'][overall_file_name.lower(
                            ).replace('.html', '_path')] = os.path.join(
                                overall_path, overall_file_name)
                    for tourment_file_name in os.listdir(team_path):
                        tourment_path = os.path.join(team_path,
                                                     tourment_file_name)
                        if os.path.isdir(tourment_path
                                         ) and tourment_file_name != 'Overall':
                            team_info['tourments'][tourment_file_name] = {}
                            for season_file_name in os.listdir(tourment_path):
                                season_path = os.path.join(
                                    tourment_path, season_file_name)
                                if os.path.isdir(season_path):
                                    summary_path = os.path.join(
                                        season_path, 'Summary.html')
                                    defensive_path = os.path.join(
                                        season_path, 'Defensive.html')
                                    offensive_path = os.path.join(
                                        season_path, 'Offensive.html')
                                    passing_path = os.path.join(
                                        season_path, 'Passing.html')
                                    detail_path = os.path.join(
                                        season_path, 'players')
                                    formation_path = os.path.join(
                                        season_path, 'Seasonal')
                                    squad_list_path = os.path.join(
                                        season_path, 'Squad List')
                                    season_info = {
                                        'summary_path': summary_path,
                                        'defensive_path': defensive_path,
                                        'offensive_path': offensive_path,
                                        'passing_path': passing_path,
                                        'detail_path': detail_path,
                                        'formation_path': formation_path,
                                        'squad_list_path': squad_list_path,
                                        'detail_stats': []
                                    }
                                    for detail_file_name in os.listdir(
                                            detail_path):
                                        if detail_file_name.endswith('.html'):
                                            detail_file_path = os.path.join(
                                                detail_path, detail_file_name)
                                            category, sub_category, accumulation_type = detail_file_name.split(
                                                '.')[0].split('-')
                                            season_info['detail_stats'].append(
                                                {
                                                    'category':
                                                    category,
                                                    'sub_category':
                                                    sub_category,
                                                    'accumulation_type':
                                                    accumulation_type,
                                                    'path':
                                                    detail_file_path
                                                })
                                    team_info['tourments'][tourment_file_name][
                                        season_file_name] = season_info
                    league_info['teams'][team_id] = team_info
            leagues[league_id] = league_info
    return leagues


def parse_characteristic(file_name):
    print 'parse_characteristic'
    print file_name
    soup = BeautifulSoup(open(file_name, 'r').read(), 'lxml')
    characteristics = {'strengths': [], 'weaknesses': [], 'style': []}
    characteristic_div = soup.find('div', {'class': 'character-card'})
    for category in ['strengths', 'weaknesses']:
        characteristics[category] = [
            {
                'desc':
                list(element.find('div').children)[2].strip(),
                'level':
                list(list(element.children)[-2].children)[1].string.strip()
            }
            for element in characteristic_div.find('div', {'class': category
                                                           }).find_all('tr')
            if len(element.findAll('td')) == 2
        ]

    style_div = [
        list(element.children)[2]
        for element in characteristic_div.find('div', {'class': 'style'})
        .find_all('li')
    ]

    characteristics['style'] = [style.strip() for style in style_div]
    return characteristics


def parse_player_stats(file_name):
    print 'parse_player_stats'
    print file_name
    soup = BeautifulSoup(open(file_name, 'r').read(), 'lxml')
    table = next(
        e for e in soup.find_all('div', {'class': 'statistics-table-tab'})
        if "display: block" in e['style'])
    thead = table.find('thead')
    headers = [e.text if e.text else 'Nation' for e in thead.find_all('th')]
    tbody = table.find('tbody', {'id': 'player-table-statistics-body'})
    stats = {}
    for tr in tbody.find_all('tr'):
        player = {}
        for i, td in enumerate(tr.find_all('td')):
            spans = td.find_all('span')
            player[headers[i]] = td.find(text=True).strip()
            if headers[i] == 'Player':
                if len(spans) == 3:
                    player['Jersey Number'] = spans[1].text.strip()
                    player['Position'] = spans[2].text.replace(',',
                                                               ' ').strip()
                else:
                    player['Jersey Number'] = spans[0].text.strip()
                    player['Position'] = spans[1].text.replace(',',
                                                               ' ').strip()

                player['Url'] = td.find('a')['href']
                player['id'] = player['Url'].split('/')[-3]
            elif headers[i] == 'Nation':
                player['Flag'] = spans[0]['class'][-1]
        stats[player['id']] = player
    legend = {}
    for th in table.find('table', {'class':
                                   'table-column-legend info'}).find_all('th'):
        if ':' in th.text:
            key, desc = th.text.split(':')
            legend[key] = desc.strip()

    data = {'stats': stats, 'legend': legend}
    return data


def parse_overall(file_name):
    print 'parse_overall'
    print file_name
    data = {}
    soup = BeautifulSoup(open(file_name, 'r').read(), 'lxml')
    table = soup.find(
        'div', {'id': 'team-stage-stats-content'}).find('tbody').find('tr')
    for col in table.find_all('tbody'):
        for row in col.find_all('tr'):
            key_element, value_element = row.find_all('td')
            if key_element.text == 'Cards':
                data['Yellow Cards'] = float(
                    value_element.find_all('span')[1].text)
                data['Red Cards'] = float(
                    value_element.find_all('span')[2].text)
            else:
                if value_element.text.endswith('%'):
                    data[key_element.text.replace(
                        'per game', ' Per Game')] = float(
                            value_element.text.strip('%')) / 100
                else:
                    data[key_element.text.replace(
                        'per game', ' Per Game')] = float(value_element.text)
    return data


def parse_fixtures(file_name):
    print 'parse_fixtures'
    print file_name
    soup = BeautifulSoup(open(file_name, 'r').read(), 'lxml')
    table = soup.find('table', {'id': 'team-fixtures'}).find('tbody')
    games = {}
    for game_col in table.find_all('tr'):
        result_a = game_col.find('td', {'class': 'form'}).find('a')
        if not result_a:
            continue
        result = result_a.text
        match_url = result_a['href']
        tournament_a = game_col.find('td', {'class': 'tournament'}).find('a')
        tournament = tournament_a['title']
        if tournament not in OFFICAL_TOURMENTS:
            continue
        tourment_url = tournament_a['href']
        date = game_col.find('td', {'class': 'date'}).text
        team_home_a = game_col.find('td', {'class': 'home'}).find('a')
        team_home_url = team_home_a['href']
        team_home_info = team_home_url.split('/')
        team_home = team_home_info[-1]
        team_home_id = team_home_info[2]

        team_away_a = game_col.find('td', {'class': 'away'}).find('a')
        team_away_url = team_away_a['href']
        team_away_info = team_away_url.split('/')
        team_away = team_away_info[-1]
        team_away_id = team_away_info[2]

        vs_goal_a = game_col.find('td', {'class': 'result'}).find('a')
        game_log_url = vs_goal_a['href']
        vs_goal = vs_goal_a.text.replace(' ', '')
        team_home_goal = vs_goal.split(':')[0]
        team_away_goal = vs_goal.split(':')[1]
        match_report_url = game_col.find(
            'td', {'class': 'right'}).find('a')['href'] if game_col.find(
                'td', {'class': 'right'}).find('a') else ''
        game_id = game_log_url.split('/')[2]
        games[game_id] = {
            'result': result,
            'match_url': match_url,
            'tournament': tournament,
            'tourment_url': tourment_url,
            'date': date,
            'team_home_url': team_home_url,
            'team_home': team_home,
            'team_home_id': team_home_id,
            'team_away_url': team_away_url,
            'team_away': team_away,
            'team_away_id': team_away_id,
            'team_home_goal': team_home_goal,
            'team_away_goal': team_away_goal,
            'game_log_url': game_log_url,
            'vs_goal': vs_goal,
            'match_report_url': match_report_url,
            'game_id': game_id
        }
    return games


def parse_formation_stats():
    formations = {}
    return {}


def load_json(file_name):
    with open(file_name) as json_data:
        d = json.load(json_data)
        return d


def write_json(file_name, json_data):
    with open(file_name, 'w') as outfile:
        json.dump(json_data, outfile)
        return json_data


def parse_teams_stats(force=False):
    league_list = get_data_list()
    data = load_json('team_stats.json')

    for league_id, league_info in league_list.iteritems():
        changed = False
        league_data = data[league_id] if data.has_key(league_id) else {
            k: league_info[k]
            for k in ('id', 'name')
        }
        league_data['teams'] = league_data['teams'] if league_data.has_key(
            'teams') else {}
        for team_id, team_info in league_info['teams'].iteritems():
            if not force and league_data['teams'].has_key(
                    str(team_id)) and str(team_id) not in ['26', '53', '276']:
                continue
            changed = True
            team_data = {k: team_info[k] for k in ('id', 'name')}
            try:
                team_data['tourments'] = {}
                for tourment_name, season_info in team_info[
                        'tourments'].iteritems():
                    tourment_data = {}
                    for season, path_list in season_info.iteritems():
                        print team_info['name']
                        print season
                        print tourment_name
                        tourment_data[season] = {}
                        # print tourment_data['force stop']
                        if not team_data.has_key(
                                'characteristic') and season == '2016-2017':
                            team_data['characteristic'] = parse_characteristic(
                                path_list['summary_path'])
                        tourment_data[season]['summary'] = parse_player_stats(
                            path_list['summary_path'])
                        tourment_data[season][
                            'defensive'] = parse_player_stats(
                                path_list['defensive_path'])
                        tourment_data[season][
                            'offensive'] = parse_player_stats(
                                path_list['offensive_path'])
                        tourment_data[season]['passing'] = parse_player_stats(
                            path_list['passing_path'])
                        detail_stats_list = []
                        for detailed_stats_info in path_list['detail_stats']:
                            detailed_stats = {
                                k: detailed_stats_info[k]
                                for k in ('category', 'sub_category',
                                          'accumulation_type')
                            }
                            detailed_stats['stats'] = parse_player_stats(
                                detailed_stats_info['path'])
                            detail_stats_list.append(detailed_stats)
                        tourment_data[season]['detailed'] = detail_stats_list
                    team_data['tourments'][tourment_name] = tourment_data
            except Exception as e:
                print e
                print "ERROR!!"
                error = load_json('parse_teams_stats_error.json')
                if not error.has_key(team_data['id']):
                    error[team_data['id']] = {}
                if not error[team_data['id']].has_key(tourment_name):
                    error[team_data['id']][tourment_name] = {}
                if 'file_name' not in locals() and 'file_name' not in globals(
                ):
                    file_name = ''
                error[team_data['id']][tourment_name][season] = {
                    'league': league_info['path'],
                    'name': team_info['path'],
                    'season': season,
                    'tourment': tourment_name,
                    'file_name': file_name,
                    'error': str(e)
                }
                write_json('parse_teams_stats_error.json', error)
                continue
            else:
                league_data['teams'][team_id] = team_data
                data[league_id] = league_data
                # write_json('team_stats.json', data)
        if changed:
            data[league_id] = league_data
            print 'Saving league data: ' + league_id
            write_json('team_stats.json', data)
            print 'Saving done'
    return data


def parse_teams_overall(force=False):
    league_list = get_data_list()
    data = load_json('teams_overall.json')
    for league_id, league_info in league_list.iteritems():
        for team_id, team_info in league_info['teams'].iteritems():
            stats = parse_overall(team_info['overall']['statistics_path'])
            fixtures = parse_fixtures(team_info['overall']['fixtures_path'])
            goals = 0
            vs_goals = 0
            results = {'w': 0, 'l': 0, 'd': 0}
            for game in fixtures.values():
                team_key = 'team_away' if team_id == game[
                    'team_away_id'] else 'team_home'
                vs_key = 'team_away' if team_key == 'team_home' else 'team_home'
                goals += int(game[team_key + '_goal'].replace('*', ''))
                vs_goals += int(game[vs_key + '_goal'].replace('*', ''))
                r = 'd' if goals == vs_goals else game['result']
                results[r] += 1
            total_games = float(sum(results.values()))
            stats['Goals Per Game'] = goals / total_games
            stats['Vs Goals Per Game'] = vs_goals / total_games
            stats['Goals'] = goals
            stats['Vs Goals'] = vs_goals
            stats['Diff Goals'] = goals - vs_goals
            stats['Total Games'] = int(total_games)
            stats['Win'] = results['w']
            stats['Lose'] = results['l']
            stats['Draw'] = results['d']
            stats['Win Percent'] = results['w'] / total_games
            stats['Lose Percent'] = results['l'] / total_games
            stats['Draw Percent'] = results['d'] / total_games
            stats['Unbeaten Percent'] = (
                results['d'] + results['w']) / total_games
            data[team_info['name']] = {
                'stats': stats,
                'fixtures': {},
                'league': league_info['name']
            }

            print 'Saving league data: ' + team_id
            write_json('teams_overall.json', data)
            print 'Saving done'
    return data


def tmp_add_season():
    for league in get_data_list().values():
        for team in league['teams'].values():
            print team['path']
            base_path = team['path']
            for tourment in team['tourments'].keys():
                path = os.path.join(base_path, tourment)
                if os.path.isdir(path):
                    files = []
                    for file_name in os.listdir(path):
                        file_path = os.path.join(path, file_name)
                        new_file_path = os.path.join(path, '2016-2017',
                                                     file_name)
                        files.append([file_path, new_file_path])
                    os.makedirs(os.path.join(path, '2016-2017'))
                    for file_path, new_file_path in files:
                        os.rename(file_path, new_file_path)


def split_json():
    print 'Start Loading All Data'
    data = load_json('team_stats.json')
    print 'End Loading All Data'
    for league_id, league_data in data.iteritems():
        file_name = 'team_stats/' + league_id + '.json'
        print 'Start: ' + file_name
        write_json(file_name=file_name, json_data=league_data)
        print 'End: ' + file_name


# print get_data_list()['2']['teams']['32']['tourments']['Premier League'][
#     '2016-2017']['passing_path']
# print parse_characteristic('teams/Germany-Bundesliga-3/Germany-Wolfsburg-33/Bundesliga/Summary.html')
# print parse_player_stats(
#     'teams/Netherlands-Eredivisie-13/Netherlands-PEC-Zwolle-868/Eredivisie/2014-2015/Summary.html'
# )['stats']  #['/Players/97752/Show/Paul-Pogba']
# parse_teams_stats()
parse_teams_overall()
# split_json()
# parse_overall(
#     'teams/England-Premier-League-2/England-Chelsea-15/Overall/Statistics.html'
# )
# print parse_fixtures(
#     'teams/England-Premier-League-2/England-Chelsea-15/Overall/Fixtures.html')[
#         1]
