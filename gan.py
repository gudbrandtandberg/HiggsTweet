import random
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

