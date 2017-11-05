import random

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

def get_expected_spread(G, seed, iterations):
    seed_spreads = [get_spread(G, seed) for j in range(iterations)]
    return sum(seed_spreads)/len(seed_spreads)
