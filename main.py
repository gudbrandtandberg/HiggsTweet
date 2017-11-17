import networkx as nx
import random
import statistics
import multiprocessing

from spread import get_expected_spread, get_expected_spread_parallel, get_marginal_gain

data_file = "Data/soc2.txt"
#data_file = "Data/higgs-social_network.edgelist"
world = [0.001, 0.01, 0.1]

def celf(G, k):
    spread_iterations = 100
    Q = celf_set_mg1_mg2(G, k, spread_iterations)
    spreads = celf_get_spreads(G, k, Q, spread_iterations)
    return spreads

import copy
def celf_set_mg1_mg2(G, k, spread_iterations):
    cur_best = None
    cur_best_G = copy.deepcopy(G)
    cur_best_spread = []
    l = len(G.nodes)
    i = 0
    for u in G.nodes:
        i += 1
        print(l, i)
        u_mg1, spread_mg1 = get_expected_spread(G, [u], spread_iterations)
        G.node[u]['mg1'] = u_mg1
        G.node[u]['prev_best'] = cur_best
#        mg2_seed = [u] if cur_best is None else [u, cur_best]
        G.node[u]['mg2'], _ = get_expected_spread(cur_best_G, [u], spread_iterations)
        if cur_best is None or G.node[u]['mg1'] > G.node[cur_best]['mg1']:
            for n in cur_best_spread:
                cur_best_G.node[n]['visited'] = False
            for s in spread_mg1:
                cur_best_G.node[s]['visited'] = True
            cur_best = u
            cur_best_spread = spread_mg1
    return sorted(G.nodes, key=lambda x: G.node[x]['mg1'], reverse=True)

def celf_get_spreads(G, k, Q, spread_iterations):
    S = []
    spreads = []
    last_seed = None
    cur_best = Q[0]
    base_spreads = [None for i in range(k)]
    while len(S) < k:
        print(len(S))
        u = Q[0]
        if G.node[u]['flag'] == len(S):
            S.append(u)
            Q.remove(u)
            last_seed = u
            spreads.append(S[:])
            continue
        elif G.node[u]['prev_best'] == last_seed:
            G.node[u]['mg1'] = G.node[u]['mg2']
        else:
            if base_spreads[len(S)] == None:
                _, base_spread = get_expected_spread(G, S, spread_iterations)
                base_spreads[len(S)] = base_spread
            base_spread = base_spreads[len(S)]
            for b in base_spread:
                G.node[b]['visited'] = True
            mg_mg1 = get_marginal_gain(G, [], [], [u], spread_iterations)
            G.node[u]['mg1'] = mg_mg1
            G.node[u]['prev_best'] = cur_best

            mg_mg2 = get_marginal_gain(G, [], [cur_best], [cur_best, u], spread_iterations)
            G.node[u]['mg2'] = mg_mg2
            for b in base_spread:
                G.node[b]['visited'] = False

            cur_best = max(u, cur_best, key=lambda x: G.node[x]['mg1'])
        G.node[u]['flag'] = len(S)

        #heapify Q
        Q.append(u)
        Q = sorted(Q, key=lambda x: G.node[x]['mg1'], reverse=True)
    return spreads

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

def get_networkx_digraph():
    G = nx.DiGraph()
    with open(data_file, "r") as f:
        nodes = []
        edges = []
        for l in f:
            line = l.split(" ")
            if len(line) == 2:
                f, t = line
                f, t = int(f), int(t)
                w = random.choice(world)
                nodes.append(f)
                nodes.append(t)
                edges.append((f, t, w))
        for node in set(nodes):
            G.add_node(node, visited=False, mg1=0, mg2=0, flag=0, prev_best=None)
        G.add_weighted_edges_from(edges)
    return G

def main():
    c = 256
    k = 5
    parallel = 8
    G = get_networkx_digraph()
    nodes, edges = G.nodes, G.edges
    print("hehi")
    spreads = celf(G, 50)
    for S in spreads:
        spread, _ = get_expected_spread(G, S, 1000, mean=True)
        print(len(S), spread)
    exit(0)
    S = []
    for i in range(1, k):
        nodes_to_try = [node for node in nodes if node not in S]
        batch_size = len(nodes_to_try) // parallel
        q = multiprocessing.Queue()
        jobs = []
        for j in range(parallel):
            p = multiprocessing.Process(
                    target=get_best_seed_nodes,
                    args=(nodes_to_try[j*batch_size:(j+1)*batch_size], S, G, q))
            jobs.append(p)
            p.start()
        best_in_batch = []
        for proc in jobs:
            best_in_batch.append(q.get())
            proc.join()

        best_node_spread, best_node = sorted(best_in_batch)[-1]
        print(i, best_node_spread, len(list(G.neighbors(best_node))))
        S.append(best_node)

if __name__ == "__main__":
    main()
