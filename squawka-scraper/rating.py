import pandas as pd
from squawka.utils import SquawkaReport
import csv

report = SquawkaReport('data/epl_32934.xml')
data = {}
for team in report.teams:
    data[team['id']] = {'info': team, 'players': {}}
for player in report.players:
    data[player['team_id']]['players'][player['id']] = {
        'info': player, 'stats': {'shots': 0, 'shots_on_target': 0, 'takeons': 0,
                                  'be_takeon': 0, 'passes_completed': 0, 'passes_failed': 0,
                                  'tackle_success': 0, 'tackle_failed': 0, 'tackle_fouled': 0,
                                  'interceptions': 0, 'clearances': 0, 'key_passes': 0,
                                  'blocked_shot': 0, 'blocked_pass': 0, 'blocked_cross': 0,
                                  'arials_won': 0, 'arials_lost': 0, 'goals': 0}}

for event in report.goals_attempts:
    if event.get('type'):
        data[event['team_id']]['players'][event['player_id']]['stats']['shots'] += 1
    if event.get('type') in ['goal', 'save']:
        data[event['team_id']]['players'][event['player_id']
                                          ]['stats']['shots_on_target'] += 1
    if event.get('type') == 'goal':
        data[event['team_id']]['players'][event['player_id']
                                          ]['stats']['goals'] += 1
d = {}
f = {}
for event in report.takeons:
    # if event['type'] == 'Success':
    #     d[event['team_id']] = d.get(event['team_id'], 0) + 1
    #     print(event['type'])
    if event['type'] == 'Success':
        data[event['team_id']]['players'][event['player_id']
                                          ]['stats']['takeons'] += 1
        data[event['other_team']]['players'][event['other_player']
                                             ]['stats']['be_takeon'] += 1

for event in report.all_passes:
    if event['type'] == 'completed':
        data[event['team_id']]['players'][event['player_id']
                                          ]['stats']['passes_completed'] += 1
    if event['type'] == 'failed':
        print(event)
        data[event['team_id']]['players'][event['player_id']
                                          ]['stats']['passes_failed'] += 1
    if event.get('assists', False):
        data[event['team_id']]['players'][event['player_id']
                                          ]['stats']['key_passes'] += 1


for event in report.tackles:
    if event['type'] == 'Success':
        data[event['tackler_team']]['players'][event['tackler']
                                               ]['stats']['tackle_success'] += 1
        d[event['team']] = d.get(event['team'], 0) + 1
    elif event['type'] == 'Failed':
        data[event['tackler_team']]['players'][event['tackler']
                                               ]['stats']['tackle_failed'] += 1
    else:
        data[event['tackler_team']]['players'][event['tackler']
                                               ]['stats']['tackle_fouled'] += 1

for event in report.interceptions:
    data[event['team_id']]['players'][event['player_id']
                                      ]['stats']['interceptions'] += 1
    print(event)

for event in report.clearances:
    data[event['team_id']]['players'][event['player_id']
                                      ]['stats']['clearances'] += 1

# for event in report.corners:
#     if event['type'] == 'Assist':
#         d[event['team']] = d.get(event['team'], 0) + 1

for event in report.blocked_events:
    data[event['team_id']]['players'][event['player_id']
                                      ]['stats'][event['type']] += 1

for event in report.crosses:
    if event['type'] == 'Assist':
        data[event['team']]['players'][event['player_id']
                                       ]['stats']['key_passes'] += 1

for event in report.headed_duals:
    team_ids = data.keys()
    team_ids.remove(event['team_id'])
    other_team = team_ids[0]
    data[event['team_id']]['players'][event['player_id']
                                      ]['stats']['arials_won'] += 1
    data[other_team]['players'][event['otherplayer']
                                ]['stats']['arials_lost'] += 1
print(d)
print(f)
