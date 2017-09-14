# -*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import numpy as np
import os
from numpy import array
import matplotlib
if 'DISPLAY' not in os.environ: matplotlib.use('Pdf')
import matplotlib.pyplot as plt
import json
import csv
import os
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist
from sklearn.cluster import AffinityPropagation
from sklearn import metrics
from sklearn.datasets.samples_generator import make_blobs
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.cluster.hierarchy import cophenet
from scipy.spatial.distance import pdist

HEADERS = [
    "Post-Up", "P&R Ball Handler", "Isolation", "Transition", "Offscreen",
    "Handoff", "Spot-Up", "P&R Roll Man", "Cut", "Putbacks"
]

# DATA_PATH = 'play_types.data'
DATA_PATH = '../csv/defensive_league_data.csv'
# DATA_PATH = 'nba_py/datasets/normalized_TeamGeneralSplits_Four Factors.csv'
PATH = 'cluster_img'


def load_data():
    f = open(DATA_PATH)
    features = []
    names = []
    max_length = 5000
    current_length = 0
    for line in f:
        if current_length >= max_length:
            print current_length
            break
        current_length += 1
        words = line.rstrip().split(',')
        # Store player names
        names.append(words[0])
        # Store features of each player
        features.append([float(i) for i in words[1:]])
    print 'Length: ' + str(len(features))
    f.close()
    print 'Shape: ' + str(array(features).shape)
    return (array(features), names)


data, names = load_data()


def cengci(data):
    X = data
    distMatrix = pdist(X)
    Z = linkage(X, 'ward')
    c, coph_dists = cophenet(Z, pdist(X))
    print c
    dendrogram(Z)


def ap(data):
    X = data
    af = AffinityPropagation(
        damping=0.8,
        max_iter=200,
        convergence_iter=15,
        preference=None,
        affinity='euclidean',
        verbose=True).fit(X)
    cluster_centers_indices = af.cluster_centers_indices_
    labels = af.labels_

    n_clusters_ = len(cluster_centers_indices)

    print('Estimated number of clusters: %d' % n_clusters_)
    # print(
    #     "Homogeneity: %0.3f" % metrics.homogeneity_score(labels_true, labels))
    # print("Completeness: %0.3f" % metrics.completeness_score(
    #     labels_true, labels))
    # print("V-measure: %0.3f" % metrics.v_measure_score(labels_true, labels))
    # print("Adjusted Rand Index: %0.3f" % metrics.adjusted_rand_score(
    #     labels_true, labels))
    # print("Adjusted Mutual Information: %0.3f" %
    #       metrics.adjusted_mutual_info_score(labels_true, labels))
    print("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(
        X, labels, metric='sqeuclidean'))


def show_result_elbow(data):
    X = data

    K = range(1, 20)
    meandistortions = []
    for k in K:
        kmeans = KMeans(n_clusters=k)
        kmeans.fit(X)
        # 求kmeans的成本函数值
        meandistortions.append(
            sum(
                np.min(cdist(X, kmeans.cluster_centers_, 'euclidean'), axis=1))
            / X.shape[0])

    plt.figure()
    plt.grid(True)
    plt1 = plt.subplot(2, 1, 1)
    plt1.plot(X[:, 0], X[:, 1], 'k.')
    plt2 = plt.subplot(2, 1, 2)

    plt2.plot(K, meandistortions, 'bx-')
    plt.show()


def show_result_score(data):
    Ks = range(1, 80)
    km = [KMeans(n_clusters=i) for i in Ks]
    score = [km[i].fit(data).score(data) for i in range(len(km))]
    plt.plot(Ks, score)
    plt.show()


def show_result_sc(data):

    X = data

    for n_cluster in range(2, 80):
        kmeans = KMeans(n_clusters=n_cluster).fit(X)
        label = kmeans.labels_
        sil_coeff = silhouette_score(X, label, metric='euclidean')
        print("For n_clusters={}, The Silhouette Coefficient is {}".format(
            n_cluster, sil_coeff))


# show_result(data)
# show_result_elbow(data)
# ap(data)
cengci(data)
# get_images(16, data)
# team_cluster()
