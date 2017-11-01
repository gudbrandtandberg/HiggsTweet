data_file = "Data/soc2.txt"
world = [1000, 100, 10]
prob_safe = 0.9

class Node:
    def __init__(self, user_id):
        self.user_id = user_id
        self.edges = []
        self.out_edges = []
        self.in_edges = []
        self.done = False

    def add_out_edge(self, edge):
        self.edges.append(edge)
        self.out_edges.append(edge)

    def add_in_edge(self, edge):
        self.edges.append(edge)
        self.in_edges.append(edge)

class Edge:
    def __init__(self, from_node, to_node, p):
        self.from_node = from_node
        self.to_node = to_node
        self.p = p
        self.tried = False

        self.from_node.add_out_edge(self)
        self.to_node.add_in_edge(self)

def get_lines():
    lines = []
    i = 0
    with open(data_file, "r") as f:
        for l in f:
            line = l.split(" ")
            if len(line) == 2:
                i += 1
#                if i == 10000000:
#                    break
                f, t = line
                lines.append((int(f), int(t)))
    return lines

def create_nodes(lines):
    nodes = {}
    edges = []
    for f,t in lines:
        if not f in nodes.keys():
            out_node = Node(f)
            nodes[f] = out_node
        if not t in nodes.keys():
            in_node = Node(t)
            nodes[t] = in_node

        out_node = nodes[f]
        in_node = nodes[t]

        edge = Edge(out_node, in_node, random.choice(world))
        edges.append(edge)
    return nodes.values(), edges

import random
import copy
import statistics

def get_spread(seeds):
    spread = []
    while len(seeds) > 0:
        frontier = []
        for s in seeds:
            spread.append(s)
            s.done = True
            for e in [edge for edge in s.out_edges if not edge.to_node.done]:
                if random.randint(1, e.p) == 1:
                    frontier.append(e.to_node)
        seeds = frontier

    for node in spread:
        node.done = False
#        for e in node.edges:
#            e.tried = False

    return len(spread)

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

def main():
    c = 256
    k = 50
    spread_iterations = 100
    lines = get_lines()
    nodes, edges = create_nodes(lines)
    print("hehi")
    print(sorted([len(n.in_edges) for n in nodes]))
    S = []
    for i in range(1, k):
        best_node = None
        best_node_spread = 0
        l = 0
        for n in [node for node in nodes if node not in S]:
            l += 1
            print(l)
            seed = S[:]
            seed.append(n)
            seed_spreads = [get_spread(seed) for j in range(spread_iterations)]
            sigma_s = sum(seed_spreads)/len(seed_spreads)
            if sigma_s > best_node_spread:
                best_node_spread = sigma_s
                best_node = n
                print(sigma_s)
        print(i, best_node_spread, len(best_node.out_edges))
        S.append(best_node)


#        seeds = [random.sample(list(nodes.values()), k) for i in range(c)]
#        for cross_generations in range(t):
#            spread = []
#            sets = []
#            for seed in seeds:
#                orig = seed[:]
#                seed_spreads = [get_spread(seed, nodes, edges) for i in range(100)]
#                sigma_s = sum(seed_spreads)/len(seed_spreads)
#                spread.append(sigma_s)
#                sets.append((orig, sigma_s))
#            print(k, len(seeds), sum(spread)/len(spread), statistics.median(spread))
#            seeds = gan(sets, nodes, c, k)

if __name__ == "__main__":
    main()


