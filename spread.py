import random
import copy
import multiprocessing

parallel = 8

def get_spread(G, seeds):
    spread = []
    while len(seeds) > 0:
        frontier = []
        for s in seeds:
            if not G.node[s]['visited']:
                G.node[s]['visited'] = True
                spread.append(s)
                for n in G.neighbors(s):
                    if not G.node[n]['visited']:
                        p = G[s][n]['weight']
                        if p > random.random():
                            frontier.append(n)
        seeds = frontier

    for s in spread:
        G.node[s]['visited'] = False

    return len(spread), spread

def get_expected_spread(G, seed, iterations, mean=False, q=None):
    seed_spreads = sorted([get_spread(G, seed) for j in range(iterations)])
    median_spread = seed_spreads[len(seed_spreads)//2]
    if q is not None:
        q.put(median_spread)
    else:
        if mean:
            s = sum([a[0] for a in seed_spreads])
            return (s/len(seed_spreads), [])
        else:
            return median_spread

def get_expected_spread_nodes(G, nodes, iterations, q):
    spreads = []
    i = 0
    for n in nodes:
        i += 1
        if i % 100 == 0:
            print(i)
        spread, _ = get_expected_spread(G, [n], iterations)
        spreads.append((n, spread))
    q.put(spreads)

def get_marginal_gain(G, base_seed, set_one, set_two, spread_iterations):
    first_seed = base_seed[:]
    second_seed = base_seed[:]

    first_seed.extend(set_one)
    second_seed.extend(set_two)

    first_expected_spread, _ = get_expected_spread(G, first_seed, spread_iterations)
    second_expected_spread, _ = get_expected_spread(G, second_seed, spread_iterations)

    return second_expected_spread - first_expected_spread

def bfs_weight(G, n):
    threshold = 0.01
    frontier = [n]
    G.node[n]['bfs'] = 1.0
    i = 0
    while len(frontier) is not 0:
        new_frontier = []
        for node in frontier:
            parent_weight = G.node[node]['bfs']
            for child in G.neighbors(node):
                puv = G[node][child]['weight']
                child_weight = G.node[child]['bfs']
                path_weight = parent_weight * puv
                if path_weight >= threshold:
                    new_frontier.append(child)
                    i += 1
                G.node[child]['bfs'] = 1-((1-child_weight)*(1-path_weight))
        print(i)
        frontier = new_frontier
