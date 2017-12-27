import networkx as nx
import random
import statistics
import multiprocessing
import copy

from heuristics import *
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
    k_spreads = []
    spread = 0
    while len(S) < k:
        u = Q[0]
        if G.node[u]['flag'] == len(S):
            print(len(S))
            S.append(u)
            k_spreads.append(S[:])
            Q.remove(u)
        else:
            _S = S[:]
            _S.append(u)
            u_spread, _ = get_expected_spread(G, _S, spread_iterations)
            G.node[u]['mg'] = u_spread - spread
            G.node[u]['flag'] = len(S)
            Q = sorted(G.nodes, key=lambda x: G.node[x]['mg'], reverse=True)
    return k_spreads

def main():
    DF = DataFiles()

    k = 100
    monte_carlo_simulations = 1000

    print("Running expected spread with k=" + str(k) + " and simulations="+str(monte_carlo_simulations))

    with open(DF.out_plot, "w") as f:
        graphs = [DF.out_period_1_activity, DF.out_period_2_activity, DF.out_all]
        for in_file in graphs:
            G = nx.read_weighted_edgelist(in_file, create_using=nx.DiGraph())
            nx.set_node_attributes(G, False, 'visited')
            nx.set_node_attributes(G, 0, 'mg')
            nx.set_node_attributes(G, 0, 'flag')

            spreads = celf(G, k, monte_carlo_simulations)
            top_k_indeg = get_top_k_indeg(G, k)
            top_k_infl = get_top_k_infl(G, k)
            plot_indeg = []
            plot_infl = []
            plot_random = []
            plot_celf = []
            for i in range(1, k+1):
                print(i)
                indeg, _ = get_expected_spread(G, top_k_indeg[:i], monte_carlo_simulations)
                infl, _ = get_expected_spread(G, top_k_infl[:i], monte_carlo_simulations)

                # Needs to sample multiple times to remove "lucky" samples
                randoms = []
                for j in range(100):
                    r, _ = get_expected_spread(G, get_random_k(G, j), monte_carlo_simulations)
                    randoms.append(r)
                random = sum(randoms)/len(randoms)
                celf_spread, _ = get_expected_spread(G, spreads[i-1], monte_carlo_simulations)

                plot_indeg.append(indeg)
                plot_infl.append(infl)
                plot_random.append(random)
                plot_celf.append(celf_spread)

            f.write(" ".join(str(x) for x in plot_indeg) + "\n")
            f.write(" ".join(str(x) for x in plot_infl) + "\n")
            f.write(" ".join(str(x) for x in plot_random) + "\n")
            f.write(" ".join(str(x) for x in plot_celf) + "\n")

if __name__ == "__main__":
    main()
