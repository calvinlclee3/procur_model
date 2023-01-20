import sys
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing

def parse_data(filename, type):

    # ****************************** COMPONENT COUNTS ******************************
    xaxis = []
    with open(filename, 'r') as fp:
        for line in fp:
            if line.startswith("X-AXIS"):
                xaxis.append(next(fp, ''))
    with open(filename, 'r') as fp:
        lines = fp.readlines()

    xlabel = xaxis[0][:xaxis[0].rfind("*")]

    xaxis = [float(line.strip()[line.rfind("=")+2:]) for line in xaxis]

    # set height of bar
    core = [float(line.strip()[line.rfind("=")+2:]) for line in lines if line.startswith("component_counts['core']")]
    io = [float(line.strip()[line.rfind("=")+2:]) for line in lines if line.startswith("component_counts['io']")]
    l3 = [float(line.strip()[line.rfind("=")+2:]) for line in lines if line.startswith("component_counts['l3']")]
    mc = [float(line.strip()[line.rfind("=")+2:]) for line in lines if line.startswith("component_counts['mc']")]

    core_normalized = preprocessing.minmax_scale(core)
    io_normalized = preprocessing.minmax_scale(io)
    l3_normalized = preprocessing.minmax_scale(l3)
    mc_normalized = preprocessing.minmax_scale(mc)

    # print(xaxis)
    # print(core)
    # print(core_normalized)
    # print(io)
    # print(io_normalized)
    # print(l3)
    # print(l3_normalized)
    # print(mc)

    # set width of bar
    barWidth = 0.2
    fig = plt.subplots(figsize =(12, 8))

    # Set position of bar on X axis
    br1 = np.arange(len(core))
    br2 = [x + barWidth for x in br1]
    br3 = [x + barWidth for x in br2]
    br4 = [x + barWidth for x in br3]
    
    # Make the plot
    plt.bar(br1, core_normalized, color ='tab:blue', width = barWidth, label ='Core Count')
    plt.bar(br2, io_normalized, color ='tab:orange', width = barWidth, label ='IO Count')
    plt.bar(br3, l3_normalized, color ='tab:green', width = barWidth, label ='L3 Count')
    plt.bar(br4, mc_normalized, color ='tab:red', width = barWidth, label ='MC Count')
    
    # Adding Xticks
    plt.title(type, fontweight ='bold', fontsize = 15)
    plt.xlabel(xlabel, fontweight ='bold', fontsize = 15)
    plt.ylabel('Number of Components', fontweight ='bold', fontsize = 15)
    plt.xticks([r + barWidth*1.5 for r in range(len(core))], xaxis)
    plt.legend()

    plt.savefig(type + '_COMPONENT_COUNTS' + '.pdf')
    plt.close()


    # ****************************** AREA ******************************
    area = [float(line.strip()[line.rfind("=")+2:]) for line in lines if line.startswith("A_die")]
    fig = plt.subplots(figsize =(12, 8))

    plt.bar(br1, area, color ='tab:orange', width = barWidth)
    plt.title(type, fontweight ='bold', fontsize = 15)
    plt.xlabel(xlabel, fontweight ='bold', fontsize = 15)
    plt.ylabel('Area (mm\u00b2)', fontweight ='bold', fontsize = 15)
    plt.xticks([r for r in range(len(core))], xaxis)
    plt.savefig(type + '_AREA' + '.pdf')
    plt.close()


    # ****************************** POWER ******************************
    power = [float(line.strip()[line.rfind("=")+2:]) for line in lines if line.startswith("P_die")]
    fig = plt.subplots(figsize =(12, 8))

    plt.bar(br1, power, color ='tab:red', width = barWidth)
    plt.title(type, fontweight ='bold', fontsize = 15)
    plt.xlabel(xlabel, fontweight ='bold', fontsize = 15)
    plt.ylabel('Power (W)', fontweight ='bold', fontsize = 15)
    plt.xticks([r for r in range(len(core))], xaxis)
    plt.savefig(type + '_POWER' + '.pdf')
    plt.close()


    # ****************************** FREQUENCY ******************************
    core_freq = [float(line.strip()[line.rfind("=")+2:]) for line in lines if line.startswith("core_freq")]
    fig = plt.subplots(figsize =(12, 8))

    plt.bar(br1, core_freq, color ='tab:green', width = barWidth)
    plt.title(type, fontweight ='bold', fontsize = 15)
    plt.xlabel(xlabel, fontweight ='bold', fontsize = 15)
    plt.ylabel('Frequency (GHz)', fontweight ='bold', fontsize = 15)
    plt.xticks([r for r in range(len(core))], xaxis)
    plt.savefig(type + '_CORE_FREQ' + '.pdf')
    plt.close()


    # ****************************** PERFORMANCE ******************************
    perf = [float(line.strip()[line.rfind("=")+2:]) for line in lines if line.startswith("perf")]
    fig = plt.subplots(figsize =(12, 8))

    print(perf)
    plt.bar(br1, perf, color ='tab:blue', width = barWidth)
    plt.title(type, fontweight ='bold', fontsize = 15)
    plt.xlabel(xlabel, fontweight ='bold', fontsize = 15)
    plt.ylabel('Performance (Gflop/s)', fontweight ='bold', fontsize = 15)
    plt.xticks([r for r in range(len(core))], xaxis)
    plt.savefig(type + '_PERF' + '.pdf')
    plt.close()




if __name__ == "__main__":
    parse_data(sys.argv[1], sys.argv[2])