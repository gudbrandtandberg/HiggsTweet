def celf_plus_plus(G, k):
    spread_iterations = 100
    Q = celf_set_mg1_mg2(G, k, spread_iterations)
    spreads = celf_get_spreads(G, k, Q, spread_iterations)
    return spreads

def celf_set_mg1_mg2(G, k, spread_iterations):
    cur_best = None
    cur_best_G = copy.deepcopy(G)
    cur_best_spread = []
    l = len(G.nodes)
    i = 0
    for u in G.nodes:
        i += 1
        print(l, i)
        u_mg1, spread_mg1 = get_expected_spread(G, [u], spread_iterations)
        G.node[u]['mg1'] = u_mg1
        G.node[u]['prev_best'] = cur_best
#        mg2_seed = [u] if cur_best is None else [u, cur_best]
        G.node[u]['mg2'], _ = get_expected_spread(cur_best_G, [u], spread_iterations)
        if cur_best is None or G.node[u]['mg1'] > G.node[cur_best]['mg1']:
            for n in cur_best_spread:
                cur_best_G.node[n]['visited'] = False
            for s in spread_mg1:
                cur_best_G.node[s]['visited'] = True
            cur_best = u
            cur_best_spread = spread_mg1
    return sorted(G.nodes, key=lambda x: G.node[x]['mg1'], reverse=True)

def celf_get_spreads(G, k, Q, spread_iterations):
    S = []
    spreads = []
    last_seed = None
    cur_best = Q[0]
    base_spreads = [None for i in range(k)]
    while len(S) < k:
        print(len(S))
        u = Q[0]
        if G.node[u]['flag'] == len(S):
            S.append(u)
            Q.remove(u)
            last_seed = u
            spreads.append(S[:])
            print(S)
            continue
        elif G.node[u]['prev_best'] == last_seed:
            G.node[u]['mg1'] = G.node[u]['mg2']
        else:
            if base_spreads[len(S)] == None:
                _, base_spread = get_expected_spread(G, S, spread_iterations)
                base_spreads[len(S)] = base_spread
            base_spread = base_spreads[len(S)]
            for b in base_spread:
                G.node[b]['visited'] = True
            mg_mg1 = get_marginal_gain(G, [], [], [u], spread_iterations)
            G.node[u]['mg1'] = mg_mg1
            G.node[u]['prev_best'] = cur_best

            mg_mg2 = get_marginal_gain(G, [], [cur_best], [cur_best, u], spread_iterations)
            G.node[u]['mg2'] = mg_mg2
            for b in base_spread:
                G.node[b]['visited'] = False

            cur_best = max(u, cur_best, key=lambda x: G.node[x]['mg1'])
        G.node[u]['flag'] = len(S)

        #heapify Q
        Q.append(u)
        Q = sorted(Q, key=lambda x: G.node[x]['mg1'], reverse=True)
    return spreads
