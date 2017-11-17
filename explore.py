import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random

G = nx.DiGraph()

G = nx.read_edgelist("./Data/higgs-social_network.edgelist", create_using=nx.DiGraph())

with open("./Data/higgs-social_network.edgelist", "r") as f:
    M = 100
    k = 1
    for e in f:
        if k > M:
            break
            
        (m, n) = e.split(" ")
        m = int(m); n = int(n)
        print(m, n)
        G.add_edge(m, n)
        k += 1

#nx.draw(G)


print("Graph loaded:")

#plt.plot(nx.degree_histogram(G))
#plt.title("Degree Histogram")
#plt.show()

p = np.random.uniform(size=(1, M))

nx.set_edge_attributes(G, p)
