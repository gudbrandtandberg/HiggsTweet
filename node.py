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

