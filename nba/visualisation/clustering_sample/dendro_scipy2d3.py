#!/usr/bin/python

# Load required modules
import pandas as pd
import scipy.spatial
import scipy.cluster
import numpy as np
import json
import matplotlib.pyplot as plt

# DATA_PATH = '../play_styles.csv'
# DATA_PATH = '../csv/league_data.csv'
DATA_PATH = '../../nba_py/datasets/normalized_TeamGeneralSplits_Four Factors.csv'

PATH = 'cluster_img'


def load_data():
    f = open(DATA_PATH)
    features = []
    names = []
    max_length = 1000
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
        features.append([float(i.split('(')[0]) for i in words[1:]])
    print 'Length: ' + str(len(features))
    f.close()
    print 'Shape: ' + str(np.array(features).shape)
    return (np.array(features), names)


data, names = load_data()

clusters = scipy.cluster.hierarchy.linkage(data, method='ward')
T = scipy.cluster.hierarchy.to_tree(clusters, rd=False)
c, coph_dists = scipy.cluster.hierarchy.cophenet(
    clusters, scipy.spatial.distance.pdist(data))
print c
# Create dictionary for labeling nodes by their IDs
labels = list(names)
id2name = dict(zip(range(len(labels)), labels))

# Draw dendrogram using matplotlib to scipy-dendrogram.pdf
scipy.cluster.hierarchy.dendrogram(
    clusters, labels=labels, orientation='right')
plt.savefig("scipy-dendrogram.png")


# Create a nested dictionary from the ClusterNode's returned by SciPy
def add_node(node, parent):
    # First create the new node and append it to its parent's children
    newNode = dict(node_id=node.id, children=[])
    parent["children"].append(newNode)

    # Recursively add the current node's children
    if node.left: add_node(node.left, newNode)
    if node.right: add_node(node.right, newNode)


# Initialize nested dictionary for d3, then recursively iterate through tree
d3Dendro = dict(children=[], name="Root1")
add_node(T, d3Dendro)


# Label each node with the names of each leaf in its subtree
def label_tree(n, hide_names=False):
    # If the node is a leaf, then we have its name
    if len(n["children"]) == 0:
        leafNames = [id2name[n["node_id"]]]

    # If not, flatten all the leaves in the node's subtree
    else:
        leafNames = reduce(lambda ls, c: ls + label_tree(c), n["children"], [])

    # Delete the node id since we don't need it anymore and
    # it makes for cleaner JSON
    del n["node_id"]

    # Labeling convention: "-"-separated leaf names
    if hide_names:
        if len(leafNames) > 1:
            n["name"] = name = ''
        else:
            n["name"] = name = "-".join(sorted(map(str, leafNames)))
    else:
        n["name"] = name = "-".join(sorted(map(str, leafNames)))

    return leafNames


label_tree(d3Dendro["children"][0], hide_names=True)

# Output to JSON
json.dump(d3Dendro, open("d3-dendrogram.json", "w"), sort_keys=True, indent=4)
