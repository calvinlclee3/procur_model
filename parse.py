import sys
import numpy as np
import pandas as pd
from pandas import Series, DataFrame
import matplotlib.pyplot as plt


def parse_data(filename):
    name = filename.split(".")[0]

    # set width of bar
    barWidth = 0.1
    fig = plt.subplots(figsize =(12, 8))
    
    # set height of bar
    core = [12, 30, 1, 8, 12, 30, 1, 8]
    io = [12, 30, 1, 8, 12, 30, 1, 8]
    l3 = [12, 30, 1, 8, 12, 30, 1, 8]
    mc = [12, 30, 1, 8, 12, 30, 1, 8]
    
    # Set position of bar on X axis
    br1 = np.arange(len(core))
    br2 = [x + barWidth for x in br1]
    br3 = [x + barWidth for x in br2]
    br4 = [x + barWidth for x in br3]
    
    # Make the plot
    plt.bar(br1, core, color ='tab:blue', width = barWidth, label ='Core Count')
    plt.bar(br2, io, color ='tab:orange', width = barWidth, label ='IO Count')
    plt.bar(br3, l3, color ='tab:green', width = barWidth, label ='L3 Count')
    plt.bar(br4, mc, color ='tab:red', width = barWidth, label ='MC Count')
    
    # Adding Xticks
    plt.xlabel('Area (mm\u00b2)', fontweight ='bold', fontsize = 15)
    plt.ylabel('Number of Components', fontweight ='bold', fontsize = 15)
    plt.xticks([r + barWidth*1.5 for r in range(len(core))], [12, 30, 1, 8, 12, 30, 1, 8])
    
    plt.legend()
    print(br1)
    print(br2)
    print(br3)
    print(br4)
    print([r + barWidth*1.5 for r in range(len(core))])
    plt.savefig(name + '.pdf')





if __name__ == "__main__":
    parse_data(sys.argv[1])