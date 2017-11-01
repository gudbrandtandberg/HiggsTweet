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
        for s in [s for s in seeds if s not in spread]:
            spread.append(s)
            for n in [n for n in G.neighbors(s) if n not in spread]:
                p = G[s][n]['weight']
                if random.randint(1, p) == 1:
                    frontier.append(n)
        seeds = frontier

    return len(spread)

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
        G.add_nodes_from(set(nodes))
        G.add_weighted_edges_from(edges)
    return G

def main():
    c = 256
    k = 50
    parallel = 8
    G = get_networkx_digraph()
    nodes, edges = G.nodes, G.edges
    print("hehi")
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
