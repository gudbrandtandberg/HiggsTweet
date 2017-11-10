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
                        if random.randint(1, p) == 1:
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

def get_expected_spread_parallel(G, seed, iterations):
    q = multiprocessing.Queue()
    jobs = []
    for j in range(parallel):
        p = multiprocessing.Process(
                target=get_expected_spread,
                args=(G, seed, iterations//parallel, q))
        jobs.append(p)
        p.start()
    best_in_batch = []
    for proc in jobs:
        best_in_batch.append(q.get())
    for proc in jobs:
        proc.join()
    seed_spreads = sorted(best_in_batch)
    median_spread = seed_spreads[len(seed_spreads)//2]
    return median_spread

def get_marginal_gain(G, base_seed, set_one, set_two, spread_iterations):
    first_seed = base_seed[:]
    second_seed = base_seed[:]

    first_seed.extend(set_one)
    second_seed.extend(set_two)

    first_expected_spread, _ = get_expected_spread(G, first_seed, spread_iterations)
    second_expected_spread, _ = get_expected_spread(G, second_seed, spread_iterations)

    return second_expected_spread - first_expected_spread
