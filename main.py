import networkx as nx
import random
import statistics
import multiprocessing
import copy

from spread import get_expected_spread, get_expected_spread_nodes, get_marginal_gain

data_file = "Data/soc2.txt"
#data_file = "Data/higgs-social_network.edgelist"
world = [0.001, 0.01, 0.1]
world = [0.1, 0.3, 0.06]
world = [1.0]

def celf(G, k, spread_iterations):
    Q = celf_get_Q(G, spread_iterations)
    return celf_get_spreads(G, k, Q, spread_iterations)

def celf_get_Q(G, spread_iterations):
    q = multiprocessing.Queue()
    jobs = []
    parallel = 8
    batch_size = len(G.nodes)//parallel
    for j in range(parallel):
        nodes_for_batch = list(G.nodes)[j*batch_size:(j+1)*batch_size]
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

def get_best_seed_nodes(nodes_to_try, base_seed, G, q):
    spread_iterations = 100
    best_node = None
    best_node_spread = 0
    for n in nodes_to_try:
        seed = base_seed[:]
        seed.append(n)
        seed_spreads = [get_spread(G, seed)[0] for j in range(spread_iterations)]
        sigma_s = sum(seed_spreads)/len(seed_spreads)
        if sigma_s > best_node_spread:
            best_node_spread = sigma_s
            best_node = n
    q.put((best_node_spread, best_node))

def get_networkx_digraph(data_file):
    G = nx.DiGraph()
    append_data_to_digraph(G, data_file)
    return G

def append_data_to_digraph(G, data_file):
    with open(data_file, "r") as f:
        nodes = []
        edges = []
        for l in f:
            line = l.split(" ")
            if len(line) >= 2:
                f, t = int(line[0]), int(line[1])
                w = random.choice(world)
                nodes.append(f)
                nodes.append(t)
                edges.append((t, f, w))
        for node in set(nodes):
            G.add_node(node, visited=False, mg=0)
        G.add_weighted_edges_from(edges)
    return G

def main():
    c = 256
    k = 200
    parallel = 8
    data_file = "Data/higgs-reply_network.edgelist"
    data_file2 = "Data/higgs-mention_network.edgelist"
    data_file3 = "Data/higgs-retweet_network.edgelist"
    G = get_networkx_digraph(data_file)
    append_data_to_digraph(G, data_file2)
    append_data_to_digraph(G, data_file3)

    Q = celf_get_Q(G, 1)
    for node in Q:
        print(G.nodes[node]['mg'], node)

#    celf(G, k, 100)

if __name__ == "__main__":
    main()
