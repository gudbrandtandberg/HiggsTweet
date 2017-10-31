data_file = "Data/soc.txt"
world = [1000, 100, 10]

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
    return nodes, edges

import random
import copy
import statistics

def get_spread(seeds, nodes, edges):
    changed = True
    while changed:
        changed = False
        for s in [node for node in seeds if not node.done]:
            changed = True
            s.done = True
            nodes_to_add = []
            for e in [edge for edge in s.out_edges if not edge.tried \
                                                  and not edge.to_node.done]:
                e.tried = True
                if random.randint(1, e.p) == 1:
                    nodes_to_add.append(e.to_node)
        seeds.extend(nodes_to_add)

    for node in seeds:
        node.done = False
        for e in node.edges:
            e.tried = False

    return len(seeds)

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
    t = 100
    lines = get_lines()
    nodes, edges = create_nodes(lines)
    print("hehi")
    S = []
    for k in range(16, 17):
        orig = S[:]

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


