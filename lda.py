# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import numpy as np
import json
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.datasets.samples_generator import make_classification
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from sklearn.cluster import AffinityPropagation
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist
# DATA_PATH = 'play_types.data'
DATA_PATH = 'csv/league_data.csv'
PATH = 'cluster_img'
defensive_sides = ['DL', 'DR']
offensive_sides = ['AML', 'ML', 'MR', 'AMR']
defensive_centers = ['DC', 'DEFENDER']
keeper = ['KEEPER', 'GOALKEEPER', 'GK']
midfielders = ['DMC', 'MC', 'AMC', 'MIDFIELDER']
forwards = ['FW', 'FORWARD']
simple_positions = {
    'defensive_sides': defensive_sides,
    'offensive_sides': offensive_sides,
    'defensive_centers': defensive_centers,
    'keeper': keeper,
    'midfielders': midfielders,
    'forwards': forwards
}


def load_json(file_name):
    with open(file_name) as json_data:
        d = json.load(json_data)
        return d


def get_positions(data):
    result = {}
    positions = []
    for item in data:
        simple_position = []
        for position in get_position(item):
            for key, value in simple_positions.iteritems():
                if position in value:
                    simple_position.append(key)
        simple_position = list(set(simple_position))
        list.sort(simple_position)
        result[item] = ','.join(simple_position)
        positions.append(result[item])
    positions = list(set(positions))
    list.sort(positions)
    for item in data:
        result[item] = positions.index(result[item])
    print len(data)
    print positions
    print len(positions)
    return result


def get_position(original_position):
    position = []
    for item in original_position.split(' '):
        if len(item.split('(')) > 1:
            main_position = item.split('(')[0]
            sides = item.split('(')[1].split(')')[0]
            for side in sides:
                position.append((main_position + side).upper())
        else:
            position.append(item.upper())
    list.sort(position)
    return position


def load_data():
    f = open(DATA_PATH)
    player_positions = load_json('data/positions.json')
    positions = get_positions(
        list(set([v['Position'] for k, v in player_positions.iteritems()])))
    classes = []
    used_positions = []
    features = []
    names = []
    max_length = 99999
    current_length = 0
    for line in f:
        if current_length >= max_length:
            print current_length
            break
        current_length += 1
        words = line.rstrip().split(',')
        # Store player names
        names.append(words[0].decode('utf-8', 'ignore'))
        classes.append(positions[player_positions[words[0].decode(
            'utf-8', 'ignore')]['Position']])
        # Store features of each player
        features.append([float(i) for i in words[1:]])
    print 'Length: ' + str(len(features))
    f.close()
    print 'Shape: ' + str(np.array(features).shape)
    print list(set(classes))
    return (np.array(features), names, classes)


def show_result_sc(data):

    X = data

    for n_cluster in range(2, 80):
        kmeans = KMeans(n_clusters=n_cluster).fit(X)
        label = kmeans.labels_
        sil_coeff = silhouette_score(X, label, metric='euclidean')
        print("For n_clusters={}, The Silhouette Coefficient is {}".format(
            n_cluster, sil_coeff))


X, names, y = load_data()
fig = plt.figure()
lda = LinearDiscriminantAnalysis(n_components=2)
lda.fit(X, y)
X_new = lda.transform(X)
show_result_sc(X_new)
# 2D
# plt.scatter(X_new[:, 0], X_new[:, 1], marker='o', c=y)

# 3D
# ax = Axes3D(fig, rect=[0, 0, 1, 1], elev=30, azim=20)
# plt.scatter(X[:, 0], X[:, 1], X[:, 2], marker='o', c=y)

# for label, x, y in zip(names, X_new[:, 0], X_new[:, 1]):
#     plt.annotate(
#         label,
#         xy=(x, y),
#         xytext=(-20, 20),
#         textcoords='offset points',
#         ha='right',
#         va='bottom',
#         bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
#         arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

# for i, txt in enumerate(names):
#     plt.annotate(txt.split('_')[0], (X_new[:, 0][i], X_new[:, 1][i]))
plt.show()
