import pandas as pd
from squawka.utils import SquawkaReport
import csv
import os
import json
from collections import defaultdict


def load_json(file_name):
    with open(file_name) as json_data:
        d = json.load(json_data)
        return d


def write_json(file_name, json_data):
    print 'writting:' + file_name
    with open(file_name, 'w') as outfile:
        json.dump(json_data, outfile)
        return json_data
    print 'writting done:' + file_name


def positions():
    results = {}
    results = defaultdict(lambda: 0, results)
    max = len(os.listdir('data'))
    print max
    for file_name in os.listdir('data'):
        if file_name.endswith('.xml'):
            report = SquawkaReport(os.path.join('data', file_name))
            if report.players:
                print report.name
                for player in report.players:
                    if player['state'] == 'playing':
                        results[','.join(
                            [player['x_loc'], player['y_loc']])] += 1
            else:
                print file_name
            max -= 1
            print max
    write_json('positions.json', dict(results))


def positions_to_csv():
    data = load_json('positions.json')
    for key, value in


positions()
