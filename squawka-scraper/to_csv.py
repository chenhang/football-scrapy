import os
import csv
from squawka.utils import export_all_stats
export_all_stats('tmp/data/', 'tmp/out/')
for file_name in os.listdir('tmp/out'):
    file_path = os.path.join('tmp', 'out', file_name)
    print("1. " + file_name)
    lines = [line.split('\n')[0].split(',') for line in open(file_path)]
    for name in lines[0]:
        print('    * ' + name + ':')
