import random

import numpy as np
import pandas as pd
import networkx as nx

class DataFiles:
    def __init__(self):
        self.in_social = "Data/higgs-social_network.edgelist"
        self.in_period_1_activity = "./Data/in_subgraphs/period_1_activity.txt"
        self.in_period_2_activity = "Data/in_subgraphs/period_2_activity.txt"

        self.out_period_1_activity = "Data/out_subgraphs/period_1_activity_graph"
        self.out_period_2_activity = "Data/out_subgraphs/period_2_activity_graph"

        self.out_period_1_all = "Data/out_subgraphs/period_1_all_graph"
        self.out_period_2_all = "Data/out_subgraphs/period_2_all_graph"

        self.out_social = "Data/out_subgraphs/social_graph"
        self.out_all = "Data/out_subgraphs/all_graph"

        self.out_plot = "plots.txt"

    def load_period_1_activity(self):
        G = load_activity_graph(self.in_period_1_activity)
        return G

    def load_period_2_activity(self):
        G = load_activity_graph(self.in_period_2_activity)
        return G

    def load_period_1_all(self):
        G = load_social_graph(self.in_social)
        append_activity_to_graph(G, self.in_period_1_activity)
        return G

    def load_period_2_all(self):
        G = load_social_graph(self.in_social)
        append_activity_to_graph(G, self.in_period_2_activity)
        return G

    def load_social(self):
        G = load_social_graph(self.in_social)
        return G

    def load_all(self):
        G = load_social_graph(self.in_social)
        append_activity_to_graph(G, self.in_period_1_activity)
        append_activity_to_graph(G, self.in_period_2_activity)
        return G

# UTILITY

def read_log(in_log):
    # without the backslash does not work. possible bug with pandas. pypy uses c-engine probably.
    # needs engine=python to avoid warning
    return pd.read_csv(in_log, delimiter="\ ", engine="python")

def load_activity_graph(in_activity):
    G = nx.MultiDiGraph()
    log = read_log(in_activity)
    for date, action in log.iterrows():
        G.add_edge(action["user1"], action["user2"], kind=action["type"])
    return G

def load_social_graph(in_social):
    G = nx.read_edgelist(in_social,
            create_using=nx.MultiDiGraph(), nodetype=int, data=(("kind", str),))
    # Add Friendship label to each edge in the loaded graph
    nx.set_edge_attributes(G, "FR", "kind")
    return G

def append_activity_to_graph(G, in_activity):
    log = read_log(in_activity)
    for date, action in log.iterrows():
        G.add_edge(action["user1"], action["user2"], kind=action["type"])
