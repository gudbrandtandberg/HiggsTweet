import networkx as nx
import random
import statistics
import multiprocessing
import copy

from spread import get_expected_spread, get_expected_spread_nodes, get_marginal_gain
from load_higgs import DataFiles

# https://codereview.stackexchange.com/questions/4872/pythonic-split-list-into-n-random-chunks-of-roughly-equal-size
def chunk(xs, n):
    ys = xs[:]
    random.shuffle(ys)
    size, leftover = divmod(len(ys), n)
    chunks = [ys[size*i : size*(i+1)] for i in range(n)]
    edge = size*n
    for i in range(leftover):
        chunks[i%n].append(ys[edge+i])
    return chunks

def celf(G, k, spread_iterations):
    Q = celf_get_Q(G, spread_iterations)
    return celf_get_spreads(G, k, Q, spread_iterations)

def celf_get_Q(G, spread_iterations):
    q = multiprocessing.Queue()
    jobs = []
    parallel = 8
    chunks = chunk(list(G.nodes), parallel)
    for j in range(parallel):
        nodes_for_batch = chunks[j]
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

def main():
    DF = DataFiles()

    k = 50
    spread_iterations = 100

    p1_activity = nx.read_weighted_edgelist(DF.out_period_1_activity,
            create_using=nx.DiGraph())
    nx.set_node_attributes(p1_activity, False, 'visited')
    nx.set_node_attributes(p1_activity, 0, 'mg')
    nx.set_node_attributes(p1_activity, 0, 'flag')

    celf(p1_activity, k, spread_iterations)

#    Q = celf_get_Q(G, 1)
#    for node in Q:
#        print(G.nodes[node]['mg'], node)

if __name__ == "__main__":
    main()
