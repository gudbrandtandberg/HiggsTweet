import matplotlib.pyplot as plt

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
