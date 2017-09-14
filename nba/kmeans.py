# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from modshogun import *
import numpy as np
from numpy import array
import matplotlib.pyplot as plt
import json
import csv
import os
HEADERS = [
    "Post-Up", "P&R Ball Handler", "Isolation", "Transition", "Offscreen",
    "Handoff", "Spot-Up", "P&R Roll Man", "Cut", "Putbacks"
]

DATA_PATH = 'play_types.data'

PATH = 'cluster_img'


def load_data():
    f = open(DATA_PATH)
    features = []
    names = []
    for line in f:
        words = line.rstrip().split(',')
        # Store player names
        names.append(words[0])
        # Store features of each player
        features.append([float(i) for i in words[1:]])

    f.close()
    print len(names)
    return (array(features).T, names)


data, names = load_data()


def train_kmeans(k, data):
    train_features = RealFeatures(data)

    # calculate euclidean distance of features
    distance = EuclideanDistance(train_features, train_features)

    # initialize KMeans++ object
    kmeans = KMeans(k, distance, True)

    # training kmeans
    kmeans.train(train_features)

    # labels for data points
    result = kmeans.apply()
    centers = kmeans.get_cluster_centers()
    radiuses = kmeans.get_radiuses()

    return result, centers, radiuses


def show_result(data):
    ys = []
    xs = []

    player_count = len(data[0])
    for k in range(5, 28):
        print k
        xs.append(k)
        _ys = []
        for i in range(1, 30):
            result, centers, radiuses = train_kmeans(k, data)
            for player_i in range(0, player_count):
                cluster_i = int(result[player_i])
                center = array([x[cluster_i] for x in centers])
                player = array([y[player_i] for y in data])
                _ys.append(np.sum((center - player)**2))
        ys.append(sum(_ys) / player_count)
    import matplotlib.pyplot as plt

    plt.plot(xs, ys)
    plt.show()


def get_result(k, data):
    centers = []
    result = []
    while True:
        result, centers, radiuses = train_kmeans(k, data)
        r = sum(radiuses) / k
        print r
        if r < 0.348:
            print(r)
            break
    return result, centers


def save_result(k, data):
    result, centers = get_result(k, data)
    with open('centers.json', 'w') as outfile:
        json.dump(centers.tolist(), outfile)

    output = {}
    for i, name in enumerate(names):
        output[name] = int(result[i])

    with open('result.json', 'w') as outfile:
        json.dump(output, outfile)


def players(names, result, index):
    players = []
    for i, name in enumerate(names):
        if int(result[i]) == index:
            info = name.split('_')
            merged_name = '-'.join([info[0], info[2]])
            split_name = [info[0], info[2]]
            players.append(split_name)
    print(len(players))
    return players


def draw_clusters(result, centers):
    size = len(HEADERS)
    ind = np.arange(size)
    width = 0.5
    headers = []
    # colors = [(min(x/10.0, 1), x/20.0, 0.55) for x in range(1,21,2)]
    colors = plt.cm.RdYlBu(np.linspace(0, 1, size))
    for i in range(size):
        headers.append(str(i) + ': ' + HEADERS[i])
    fig, subs = plt.subplots(
        nrows=3, ncols=5, figsize=(16, 7), sharex=True, sharey=True)
    ax = []
    for c in range(len(subs)):
        for r in range(len(subs[0])):
            ax.append(subs[c][r])
    # ax[0].set_ylabel('Freq Rating')
    ax[0].set_xticks(ind)
    ax[0].set_yticks([])
    player_names = []
    for index in range(0, 15):
        rects = ax[index].bar(
            ind, [values[index] for values in centers], width, color=colors)
        ax[index].set_title("Cluster " + str(index + 1))
        ax[index].set_ylim([0, 1])
        player_names.append(players(names, result, index))

    ax[0].legend(
        rects, headers, ncol=2, loc='upper right', bbox_to_anchor=(0, 1.1))
    fig.subplots_adjust(hspace=0.1)
    fig.tight_layout(rect=(0.3, 0, 1, 1))
    bax = fig.add_subplot(2, 2, 3)
    rects = bax.bar(
        ind, [values[0] for values in centers], width, color=colors)
    plt.show()


def draw_cluster(result, centers, index, save_file=True):
    size = len(HEADERS)
    ind = np.arange(size)
    width = 0.5
    headers = []
    # colors = [(min(x/10.0, 1), x/20.0, 0.55) for x in range(1,21,2)]
    colors = plt.cm.RdYlBu(np.linspace(0, 1, size))
    for i in range(size):
        headers.append(str(i) + ': ' + HEADERS[i])
    player_names = players(names, result, index)
    if save_file:
        window_size = (16, 10)
    else:
        window_size = (16, 7)
    fig, ax = plt.subplots(figsize=window_size)
    ax.set_xticks(ind)
    ax.set_yticks([])
    ax.set_ylim([0, 1])
    rects = ax.bar(
        ind, [values[index] for values in centers], width, color=colors)
    title = "Cluster " + str(index + 1)
    ax.set_title(title)

    ax.legend(
        rects, headers, ncol=3, loc='upper left')  #, bbox_to_anchor = (0,1.1))
    rows = 60
    player_size = len(player_names)
    cols = player_size / rows + 1
    while cols > 3:
        rows += 1
        cols = player_size / rows + 1
    while cols < 2:
        rows -= 1
        cols = player_size / rows + 1

    cells = [[['', ''] for c in range(cols)] for r in range(rows)]
    current_pos = 0
    for c in range(cols):
        for r in range(rows):
            if current_pos < len(player_names):
                cells[r][c] = player_names[current_pos]
            current_pos += 1
    for r in range(rows):
        cells[r] = [v for e in cells[r] for v in e]
    col_headers = [
        'player' if (i % 2) == 0 else 'team' for i in range(2 * cols)
    ]
    table = ax.table(
        cellText=cells,
        colLabels=col_headers,
        cellLoc='left',
        bbox=(1, 0, 1.1, 1),
        colLoc='left')

    fig.tight_layout(rect=(0, 0, 0.5, 1))

    table.set_fontsize(24)
    if save_file:
        plt.savefig(os.path.join(PATH, title + '.svg'))
    else:
        plt.show()


def get_images(k, data):
    result, centers = get_result(k, data)
    for i in range(k):
        # draw_cluster(result, centers, i)
        print('File saved: ' + str(i + 1) + ' of ' + str(k))

    with open('cluster_result/centers.json', 'w') as outfile:
        json.dump(centers.tolist(), outfile)

    output = {}
    _result = []
    size = 0
    for i, name in enumerate(names):
        output[name] = int(result[i])
    for cluster in result:
        size += 1
        _result.append(int(cluster))
    print size
    with open('cluster_result/result.json', 'w') as outfile:
        json.dump(_result, outfile)
    with open('cluster_result/players.json', 'w') as outfile:
        json.dump(output, outfile)
    print(len(_result))
    print(len(names))
    print(len(output))

    print 'cp cluster_img/* ~/chenhang.github.io/mu/cluster/img'


def team_cluster():
    radar_data = []
    with open('cluster_result/result.json') as data_file:
        result = json.load(data_file)
    with open('cluster_result/centers.json') as data_file:
        centers = json.load(data_file)
    with open('cluster_result/players.json') as data_file:
        players = json.load(data_file)
    for line in open(DATA_PATH):
        row = line.split('\n')[0].split(",")
        key = row[0].decode('utf-8')
        info = key.split('_')
        name = info[0]
        team = info[2]
        season = info[-1]
        values = []
        for value in row[1:]:
            values.append(str(value) + '(' + str(value) + ')')
        radar_data.append([name, team, players[key], season] + values)
    writer = csv.writer(open('cluster_result/kmeans_league_data.csv', 'wb'))
    for item in radar_data:
        writer.writerow(item)


# show_result(data)
get_images(16, data)
team_cluster()
