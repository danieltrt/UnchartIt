import numpy as np
import matplotlib.pyplot as plt
import time
import os
plt.rcdefaults()


class PlotGenerator:

    def __init__(self):
        self.fig_n = int(time.time())

    def gen_bar_plot(self, table, title):
        self.fig_n += 1

        cols = table.get_active_cols()
        objects = cols[0]
        y_pos = np.arange(len(objects))
        performance = cols[1]

        plt.bar(y_pos, performance, align='center', alpha=0.5)
        plt.xticks(y_pos, objects)

        plt.xlabel(table.col_names[0])
        plt.ylabel(table.col_names[1])
        plt.title(title)

        file_path = os.path.dirname(__file__) + "/../../media/{}.png".format(self.fig_n)
        plt.savefig(file_path)
        plt.figure(self.fig_n)
        return "{}.png".format(self.fig_n)
