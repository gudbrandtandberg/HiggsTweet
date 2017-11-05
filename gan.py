import random
prob_safe = 0.9

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

def create_child_set(a, b):
    c = [node for node in a if node not in b]
    child = []
    for i in range(len(b)):
        if i < len(b) // 2:
            child.append(a[i])
        else:
            child.append(b[i])
    return child

def mutate_set(seed_set, G, p):
    for i in range(len(seed_set)):
        if random.randint(1, p) == 1:
            seed_set[i] = random.choice(list(G.nodes))
    return seed_set

def gan(sorted_spreads):
    elites = sorted_spreads[:2]
    while len(elites) < len(sorted_spreads):
        a, b = random.sample(sorted_spreads, 2)
        elites.append(create_child_set(a, b))
    return elites

