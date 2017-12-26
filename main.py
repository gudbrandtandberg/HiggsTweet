import networkx as nx
import random
import statistics
import multiprocessing
import copy

from spread import get_expected_spread, get_expected_spread_nodes, get_marginal_gain
from heur import heuristic
from load_higgs import DataFiles

def celf(G, k, spread_iterations):
    Q = celf_get_Q(G, spread_iterations)
    return celf_get_spreads(G, k, Q, spread_iterations)

def celf_get_Q(G, spread_iterations):
    q = multiprocessing.Queue()
    jobs = []
    parallel = 8
    nodes = G.nodes()
    batch_size = len(nodes)//parallel
    for j in range(parallel):
        nodes_for_batch = list(nodes)[j*batch_size:(j+1)*batch_size]
        p = multiprocessing.Process(
                target=get_expected_spread_nodes,
                args=(G, nodes_for_batch, spread_iterations, q))
        jobs.append(p)
        p.start()
    best_in_batch = []
    for proc in jobs:
        best_in_batch.append(q.get())
    for proc in jobs:
        proc.join()

    for batch in best_in_batch:
        for u, spread in batch:
            G.node[u]['mg'] = spread
    return sorted(G.nodes, key=lambda x: G.node[x]['mg'], reverse=True)

def celf_get_spreads(G, k, Q, spread_iterations):
    S = []
    spread = 0
    while len(S) < k:
        u = Q[0]
        if G.node[u]['flag'] == len(S):
            S.append(u)
            spread, _ = get_expected_spread(G, S, 1000)
            print(len(S), spread)
            Q.remove(u)
        else:
            _S = S[:]
            _S.append(u)
            u_spread, _ = get_expected_spread(G, _S, spread_iterations)
            G.node[u]['mg'] = u_spread - spread
            G.node[u]['flag'] = len(S)
            Q = sorted(G.nodes, key=lambda x: G.node[x]['mg'], reverse=True)
    return S

def create_digraph(G):
    """
    G is a typed multidigraph. 
    Build a weighted digraph by combining parallel edges
    """
    kind_weights = {"RT" : 0.01, "RE" : 0.01, "RT" : 0.01, "MT" : 0.01, "FR" : 0.00}

    D = nx.DiGraph()
    D.add_nodes_from(G)
    nx.set_edge_attributes(D, 0.0, "weight")

    for u in G:
        for v in G.predecessors(u):
            edges = dict(G[v][u])
            weight = 0.0
            for edge in edges.values():
                kind = edge["kind"]
                weight += kind_weights[kind]
            weight = np.min((weight, 1.0))
            if weight != 0:
                D.add_edge(u, v, weight=weight)
    return D

def main():
    DF = DataFiles()

    k = 50
    spread_iterations = 100

    p1_activity = nx.read_weighted_edgelist(DF.out_period_1_activity)
    nx.set_node_attributes(p1_activity, False, 'visited')
    nx.set_node_attributes(p1_activity, 0, 'mg')
    nx.set_node_attributes(p1_activity, 0, 'flag')

    celf(p1_activity, k, spread_iterations)

#    Q = celf_get_Q(G, 1)
#    for node in Q:
#        print(G.nodes[node]['mg'], node)

if __name__ == "__main__":
    main()
