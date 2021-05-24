import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import random as rd
import threading

# use ggplot style for more sophisticated visuals
plt.style.use('ggplot')

def animate(i,simulation: 'Simulation'):
    
    while simulation.lock.locked():
        pass

    simulation.lock.acquire()
    x1 = range(len(simulation.blobs_num_over_time))
    y1 = simulation.blobs_num_over_time


    plt.cla()

    plt.plot(x1, y1, label='population')

    plt.legend(loc='upper left')
    plt.tight_layout()
    
    simulation.lock.release()


if __name__ == "__main__":
    x_vals = []
    y_vals = []

    ani = FuncAnimation(plt.gcf(), animate, fargs=(x_vals,y_vals,), interval=1000)

    plt.tight_layout()
    plt.show()