import random
import numpy as np

def get_top_k_indeg(G, k):
    return [x[0] for x in sorted(G.in_degree(), key=lambda x: x[1])[:k]]

def get_random_k(G, k):
    return random.sample(list(G.nodes()), k)

def get_top_k_infl(G, k):
    total_infl = {}
    for n in G.nodes:
        for s in G.neighbors(n):
            if n not in total_infl.keys():
                total_infl[n] = 0
            total_infl[n] += G[n][s]['weight']
    return sorted(total_infl.keys(), key=lambda x: total_infl[x])[:k]
