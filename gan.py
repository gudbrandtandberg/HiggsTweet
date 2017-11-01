def create_child_set(a, b, k):
    c = [node for node in a if node not in b]
    c.extend(b)
    return random.sample(list(c), k)

def gan(sets, nodes, set_amount, k):
    good_sets = int(set_amount**(1/2))
    best_seeds = [a[0] for a in sorted(sets, key=lambda x: x[1])[len(sets)-good_sets:]]
    sets_to_try = []
    safe_cross = int(k*prob_safe)
    rand_cross = k - safe_cross
    print(safe_cross, rand_cross)
    for i in range(len(best_seeds)):
        for j in range(i, len(best_seeds)):
            cross_set = create_child_set(best_seeds[i], best_seeds[j], safe_cross)
            cross_set.extend(random.sample(list(nodes.values()), rand_cross))
            sets_to_try.append(cross_set)
    return sets_to_try
