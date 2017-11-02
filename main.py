import networkx as nx
import random
import statistics
import multiprocessing

data_file = "Data/soc2.txt"
#data_file = "Data/higgs-social_network.edgelist"
world = [1000, 100, 10]
prob_safe = 0.9

def get_spread(G, seeds):
    spread = []
    while len(seeds) > 0:
        frontier = []
        for s in seeds:
            if not G.node[s]['visited']:
                G.node[s]['visited'] = True
                spread.append(s)
                for n in G.neighbors(s):
                    p = G[s][n]['weight']
                    if random.randint(1, p) == 1:
                        frontier.append(n)
        seeds = frontier

    for s in spread:
        G.node[s]['visited'] = False

    return len(spread)

def celf(G, k):
    spread_iterations = 100
    S = []
    Q = []
    last_seed = None
    cur_best = None
    l = len(G.nodes)
    i = 0
    for u in G.nodes:
        i += 1
        print(l, i)
        G.node[u]['mg1'] = get_expected_spread(G, [u], spread_iterations)
        G.node[u]['prev_best'] = cur_best
        mg2_seed = [u]
        if cur_best is not None:
            mg2_seed = [u, cur_best]
        G.node[u]['mg2'] = get_expected_spread(G, mg2_seed, spread_iterations)
        Q.append(u)
        cur_best_mg1 = 0
        for node in G.nodes:
            if G.node[node]['mg1'] > cur_best_mg1:
                cur_best = node
    Q = sorted(Q, key=lambda x: G.node[x]['mg1'], reverse=True)
    print("for done")
    spreads = []
    while len(S) < k:
        print(len(S))
        u = Q[0]
        if G.node[u]['flag'] == len(S):
            S.append(u)
            Q.remove(u)
            last_seed = u
            continue
        elif G.node[u]['prev_best'] == last_seed:
            G.node[u]['mg1'] = G.node[u]['mg2']
        else:
            tmpS = S[:]
            tmpS.append(u)
            expected_spread_u = get_expected_spread(G, tmpS, spread_iterations) 
            marginal_gain = expected_spread_u - get_expected_spread(G, S, spread_iterations)
            G.node[u]['prev_best'] = cur_best
            curbestS = S[:]
            curbestS.append(cur_best)
            G.node[u]['mg2'] = expected_spread_u - get_expected_spread(G, curbestS, spread_iterations)
        G.node[u]['flag'] = len(S)

        #update cur_best
        cur_best_mg1 = 0
        for u in G.nodes:
            if G.node[u]['mg1'] > cur_best_mg1:
                cur_best = u
        #heapify Q
        Q.append(u)
        Q = sorted(Q, key=lambda x: G.node[x]['mg1'], reverse=True)
        spreads.append(S[:])
    return spreads

def get_expected_spread(G, seed, iterations):
    seed_spreads = [get_spread(G, seed) for j in range(iterations)]
    return sum(seed_spreads)/len(seed_spreads)

def get_best_seed_nodes(nodes_to_try, base_seed, G, q):
    spread_iterations = 100
    best_node = None
    best_node_spread = 0
    for n in nodes_to_try:
        seed = base_seed[:]
        seed.append(n)
        seed_spreads = [get_spread(G, seed) for j in range(spread_iterations)]
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

from gan import gan, mutate_set
def gan_main():
    c = 100
    k = 10
    population = 100
    G = get_networkx_digraph()
    nodes, edges = G.nodes, G.edges
    print("hehi")
    spreads = []
    for i in range(population):
        S = random.sample(nodes, k)
        Sigma_S = get_expected_spread(G, S, c)
        spreads.append((Sigma_S, S))
    print(sum([a[0] for a in spreads])/len(spreads))
    best_spread = [a[1] for a in sorted(spreads, reverse=True)]

    for i in range(1000):
        children = gan(best_spread)
        children = [mutate_set(child, G, 10) for child in children]
        children_spreads = [(get_expected_spread(G, child, c), child) for child in children]
        best_spread = [a[1] for a in sorted(spreads, reverse=True)]
        print(sum([a[0] for a in children_spreads])/len(children_spreads))

def main():
    c = 256
    k = 5
    parallel = 8
    G = get_networkx_digraph()
    nodes, edges = G.nodes, G.edges
    print("hehi")
    spreads = celf(G, 50)
    for S in spreads:
        print(len(S), get_expected_spread(G, S, 100))
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
