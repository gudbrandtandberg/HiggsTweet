import matplotlib.pyplot as plt
from load_higgs import DataFiles

def plot_expected_spread():
    DF = DataFiles()
    with open(DF.out_plot, "r") as f:
        lines = f.readlines()
        indeg, infl, random, celf = [l.split(" ") for l in lines]
        plt.plot(indeg)
        plt.plot(infl)
        plt.plot(random)
        plt.plot(celf)
        plt.show()

def plot_reachable():
    with open("out2", "r") as f:
        lines = f.read()
        values = {}
        for line in lines.split("\n"):
            if len(line.split(" ")) == 2:
                amt = int(line.split(" ")[0])
                if amt not in values.keys():
                    values[amt] = 0
                values[amt] += 1
            else:
                print(line)
        x, y = [], []
        for key in values.keys():
            x.append(key)
            y.append(values[key])
        plt.scatter(x, y)
        plt.show()

if __name__ == "__main__":
    plot_expected_spread()
