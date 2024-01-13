from matplotlib import pyplot as plt
import numpy as np

data = np.genfromtxt("./gain-bp.csv", delimiter=",")[1:, :]
print(data)
gain, res, bp = data[:, 0], data[:, 1], data[:, 2]

fig, ax1 = plt.subplots()

ax1.loglog(gain, res, label="résolution=f(gain)", color="blue", lw=5, alpha=0.5)
ax2 = ax1.twinx()
ax2.loglog(gain, bp, label="bande passante=f(gain)", color="red", lw=5, alpha=0.5)
ax1.set_xlabel("gain")
ax1.set_ylabel("nV/V", color="blue")
ax2.set_ylabel("mV/V", color="red")
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax2.legend(lines + lines2, labels + labels2, loc="upper right")
ax1.grid(True, which="both", linestyle="--", color="gray", linewidth=1)
plt.show()
