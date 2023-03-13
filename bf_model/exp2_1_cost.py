import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn import preprocessing
import json
from types import SimpleNamespace
import copy
import math
import argparse

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def load_data():

    # ****************************** WRITING DEFAULT VALUES ******************************
    default = {}

    # thermal parameters
    default["theta_jc"] = 0.1
    default["theta_ca"] = 0.2
    default["theta_jb"] = 0.5
    default["theta_ba"] = 1.5 
    default["T_ambient"] = 25
    default["T_j_max"] = 100

    # area of each component
    default["core_area"] = 7E-6 
    default["l1_area"] = 1E-6
    default["l2_area"] = 2E-6
    default["l3_area"] = 1E-6
    default["mc_area"] = 10E-6
    default["io_area"] = 20E-6

    # power of each component
    default["l3_power"] = 0.2
    default["io_power"] = 10

    # bump parameters
    default["bump_pitch"] = 40E-6
    default["die_voltage_nominal"] = 1.2
    default["current_per_bump"] = 520.8333333E-3
    default["mc_bump_count"] = 288
    default["io_bump_count"] = 114

    # wire parameters
    default["package_layer"] = 6
    default["link_pitch"] = 25E-6

    # memory controller parameters
    default["wires_per_mc"] = 288
    default["energy_per_wire"] = 6.697674419E-12
    default["mc_freq"] = 1600E6
    default["mc_freq_nominal"] = 1600E6
    default["mc_voltage_nominal"] = 1.2
    default["mc_power_ctrl_nominal"] = 3                     # per MC

    # performance parameters
    default["ai_app"] = 100                                  # operations / byte
    default["IPC"] = 3.175                                   # instructions / cycle
    default["capacitance_per_core"] = 2.96080965E-9          # for the core only, per core
    default["l1_capacity"] = 80E3                            # per L1 (L1 is part of the core)
    default["l2_capacity"] = 1.25E6                          # per L2 (L2 is part of the core)
    default["l3_capacity"] = 2E6                             # per "slice" of L3
    default["l3_hit_rate_nominal"] = 0.9
    default["l3_bw"] = 1E9                                   # per L3
    default["mc_bw"] = 5E9                                   # per MC
    default["workset_size"] = 50E6                           # size of the working set
    default["core_freq_min"] = 0.8E9
    default["core_freq_base_max"] = 3E9
    default["core_freq_absolute_max"] = 10E9
    default["core_freq_nominal"] = 3.6E9

    # Cost Model Parameters


    # IMPORTANT: What used to be variables in the optimization model

    # number of each component (integer)
    default["core_count"] = 12
    default["l3_count"] = 12.5
    default["mc_count"] = 2
    default["io_count"] = 1

    default["core_freq"] = 3.6E9

    with open("default.json", "w") as outfile:
        json.dump(default, outfile)

    # THIS PART CANNOT BE HAND-CODED
    # This is just an example
    cores = []
    cores.append({})
    cores[0]['name'] = "Intel Core i9-13900K"
    cores[0]['core_freq'] = 3E9
    cores[0]['core_count'] = 24
    cores[0]['core_area'] = 7E-6
    cores[0]['die_voltage_nominal'] = 1.2
    cores[0]['l1_capacity'] = 80E3
    cores[0]['l2_capacity'] = 2E6
    # cores.append({})
    # cores[1]['name'] = "Intel Core i9-13900K"
    # cores[1]['core_freq'] = 3E9
    # cores[1]['core_count'] = 12
    # cores[1]['core_area'] = 4E-6
    # cores[1]['die_voltage_nominal'] = 1.0
    # cores.append({})
    # cores[2]['name'] = "Intel Core i3-12100F"
    # cores[2]['core_freq'] = 3.3E9
    # cores[2]['core_count'] = 2
    # cores[2]['core_area'] = 9E-6
    # cores[2]['die_voltage_nominal'] = 1.4

    with open("cores.json", "w") as outfile:
        json.dump(cores, outfile)

    mems = []
    mems.append({})
    mems[0]['name'] = "DDR4-3200 theta_ca=0.26904"
    mems[0]['mc_bw'] = 1600E6 * 2 * 8
    mems[0]['mc_count'] = 4
    mems[0]['mc_area'] = 10E-6
    mems[0]['mc_freq'] = 1600E6
    mems[0]['energy_per_wire'] = 15E-12
    mems[0]['bump_pitch'] = 100E-6
    mems[0]['current_per_bump'] = 520.8333333E-3
    mems[0]['theta_ca'] = 0.26904
    mems[0]['l3_bw'] = 30E9
    mems[0]['T_j_max'] = 110
    
    mems.append({})
    mems[1]['name'] = "DDR5-4000 theta_ca=0.22732"
    mems[1]['mc_bw'] = 2000E6 * 2 * 8
    mems[1]['mc_count'] = 4
    mems[1]['mc_area'] = 10E-6
    mems[1]['mc_freq'] = 2000E6
    mems[1]['energy_per_wire'] = 15E-12
    mems[1]['bump_pitch'] = 100E-6
    mems[1]['current_per_bump'] = 520.8333333E-3
    mems[1]['theta_ca'] = 0.22732
    mems[1]['l3_bw'] = 30E9
    mems[1]['T_j_max'] = 110

    mems.append({})
    mems[2]['name'] = "DDR5-4800 theta_ca=0.18146"
    mems[2]['mc_bw'] = 2400E6 * 2 * 8
    mems[2]['mc_count'] = 4
    mems[2]['mc_area'] = 10E-6
    mems[2]['mc_freq'] = 2400E6
    mems[2]['energy_per_wire'] = 15E-12
    mems[2]['bump_pitch'] = 100E-6
    mems[2]['current_per_bump'] = 520.8333333E-3
    mems[2]['theta_ca'] = 0.18146      # 0.185 MIDLINE
    mems[2]['l3_bw'] = 30E9
    mems[2]['T_j_max'] = 110

    mems.append({})
    mems[3]['name'] = "DDR5-6400 theta_ca=0.0975"
    mems[3]['mc_bw'] = 3200E6 * 2 * 8
    mems[3]['mc_count'] = 4
    mems[3]['mc_area'] = 10E-6
    mems[3]['mc_freq'] = 3200E6
    mems[3]['energy_per_wire'] = 15E-12
    mems[3]['bump_pitch'] = 100E-6
    mems[3]['current_per_bump'] = 520.8333333E-3
    mems[3]['theta_ca'] = 0.0975      # 0.0975 MIDLINE
    mems[3]['l3_bw'] = 30E9
    mems[3]['T_j_max'] = 110

    mems.append({})
    mems[4]['name'] = "DDR5-6400 theta_ca=0.09501"
    mems[4]['mc_bw'] = 3200E6 * 2 * 8
    mems[4]['mc_count'] = 4
    mems[4]['mc_area'] = 10E-6
    mems[4]['mc_freq'] = 3200E6
    mems[4]['energy_per_wire'] = 15E-12
    mems[4]['bump_pitch'] = 100E-6
    mems[4]['current_per_bump'] = 520.8333333E-3
    mems[4]['theta_ca'] = 0.09501      # 0.0975 MIDLINE
    mems[4]['l3_bw'] = 30E9
    mems[4]['T_j_max'] = 110

    mems.append({})
    mems[5]['name'] = "HBM2 theta_ca=0.32552"
    mems[5]['mc_bw'] = 256E9
    mems[5]['mc_count'] = 4
    mems[5]['mc_area'] = 6.6831E-6
    mems[5]['mc_freq'] = 1000E6
    mems[5]['energy_per_wire'] = 3.5E-12
    mems[5]['bump_pitch'] = 40E-6
    mems[5]['current_per_bump'] = 83.3333333E-3
    mems[5]['theta_ca'] = 0.32552
    mems[5]['l3_bw'] = 30E9
    mems[5]['T_j_max'] = 110

    with open("mems.json", "w") as outfile:
        json.dump(mems, outfile)

    l3_configs = []
    for i in range(1, 51):
        l3_configs.append({"name": f"{i}x L3s", "l3_count":i})
    
    with open("l3_configs.json", "w") as outfile:
        json.dump(l3_configs, outfile)


    ai_apps = [0.25, 0.5, 1]
    workset_sizes = [100E6, 50E6, 25E6]
    app_props = []
    for ai_app in ai_apps:
        for workset_size in workset_sizes:
            app_props.append({"name": f'{ai_app} App. AI, {workset_size/1E6} MB Workset',
                              "ai_app": ai_app,
                              "workset_size": workset_size})
    
    with open("app_props.json", "w") as outfile:
        json.dump(app_props, outfile)
    

def solve(obj, perfLB, areaUB, powerUB):

    results = []

    print(f'Solving for objective {obj} with perfLB={perfLB} Gflop/s, areaUB={areaUB} mm2, powerUB={powerUB} W\n')
    
    with open("default.json", 'r') as fp:
        master_default = json.load(fp)

    with open("cores.json", 'r') as fp:
        cores = json.load(fp)

    with open("mems.json", 'r') as fp:
        mems = json.load(fp)

    with open("l3_configs.json", 'r') as fp:
        l3_configs = json.load(fp)

    with open("app_props.json", 'r') as fp:
        app_props = json.load(fp)

    for app_prop in app_props:
        for l3_config in l3_configs:
            for mem in mems:
                for core in cores:

                    # Get a new, clean copy of default
                    default = []
                    default = copy.deepcopy(master_default)

                    result = {}
                    result["design point"] = [core["name"], mem["name"], l3_config["name"], app_prop["name"]]
                    result["obj"] = obj
                    result["core"] = copy.deepcopy(core)
                    result["mem"] = copy.deepcopy(mem)
                    result["l3_config"] = copy.deepcopy(l3_config)
                    result["app_prop"] = copy.deepcopy(app_prop)
                    result["feasible"] = True

                    # Overwrite default values, but only for keys that are already in default.json
                    default.update((k, mem[k]) for k in default.keys() & mem.keys())
                    default.update((k, core[k]) for k in default.keys() & core.keys())
                    default.update((k, l3_config[k]) for k in default.keys() & l3_config.keys())
                    default.update((k, app_prop[k]) for k in default.keys() & app_prop.keys())

                    # Convert dict to namespace for readability
                    p = SimpleNamespace(**default)

                    # Set objective-dependent constraints from CLI
                    p.perfLB = perfLB * 1E9 
                    p.areaUB = areaUB * 1E-6 
                    p.powerUB = powerUB 

                    # ****************************** MODEL EQUATIONS ******************************

                    # Compute max power allowed by thermal constraint.
                    p.theta_ja = (p.theta_jc + p.theta_ca)*(p.theta_jb + p.theta_ba)/(p.theta_jc + p.theta_ca + p.theta_jb + p.theta_ba)
                    p.delta_T = p.T_j_max - p.T_ambient
                    p.P_max = p.delta_T / p.theta_ja

                    # Compute power of a memory controller.
                    p.mc_voltage = (p.mc_freq / p.mc_freq_nominal) * p.mc_voltage_nominal
                    p.mc_power_phys = p.energy_per_wire * p.mc_freq * p.wires_per_mc * (p.mc_voltage / p.mc_voltage_nominal)**2
                    p.mc_power_ctrl = (p.mc_freq / p.mc_freq_nominal) * p.mc_power_ctrl_nominal
                    p.mc_power = p.mc_power_phys + p.mc_power_ctrl

                    # Compute arithmetic intensity.
                    p.arithmetic_intensity = (p.workset_size / (p.workset_size - (p.l1_capacity + p.l2_capacity))) * p.ai_app

                    # 5% increase in core_freq -> 10% increase in core_area
                    #                          -> 2% increase in l1_area and l2_area
                    if(p.core_freq < p.core_freq_base_max):
                        p.core_area_multiplier = 1
                        p.l1l2_area_multiplier = 1
                    else:
                        p.core_area_multiplier = (p.core_freq/p.core_freq_base_max - 1)*2 + 1
                        p.l1l2_area_multiplier = (p.core_freq/p.core_freq_base_max - 1)*0.4 + 1

                    # die_voltage scales linearly with core_freq
                    p.die_voltage = (p.core_freq / p.core_freq_nominal) * p.die_voltage_nominal
                    
                    p.core_power = p.core_freq * p.capacitance_per_core * (p.die_voltage**2)

                    p.P_die  = p.core_count * p.core_power + p.io_count * p.io_power
                    p.P_die += p.l3_count   * p.l3_power   + p.mc_count * p.mc_power

                    # number of cores = number of L1 = number of L2
                    p.A_die  = p.core_count * p.core_area * p.core_area_multiplier
                    p.A_die += p.core_count * p.l1_area * p.l1l2_area_multiplier
                    p.A_die += p.core_count * p.l2_area * p.l1l2_area_multiplier
                    p.A_die += p.io_count   * p.io_area 
                    p.A_die += p.l3_count   * p.l3_area 
                    p.A_die += p.mc_count   * p.mc_area

                    p.power_bump_count = (p.P_die) / (p.die_voltage * p.current_per_bump) * 2
                    p.max_wire = 6 * math.sqrt(p.A_die / 6) * p.package_layer / p.link_pitch

                    # relative size of the working set and the L3 cache determines L3 hit rate
                    p.l3_to_workset_ratio = (p.l3_capacity * p.l3_count) / p.workset_size
                    if(p.l3_to_workset_ratio < 1):
                        p.l3_hit_rate = p.l3_hit_rate_nominal * p.l3_to_workset_ratio
                    else:
                        p.l3_hit_rate = p.l3_hit_rate_nominal

                    p.compute_throughput = p.core_freq * p.IPC * p.core_count

                    # All LD/ST go through L3. L3 misses go through main memory.
                    p.l3_bound = p.l3_bw * p.l3_count / 1
                    p.mc_bound = p.mc_bw * p.mc_count / (1 - p.l3_hit_rate)
                    p.system_bw = min(p.l3_bound, p.mc_bound)
                    
                    # Roofline Model
                    p.compute_bound = p.compute_throughput
                    p.io_bound = p.arithmetic_intensity * p.system_bw
                    p.perf = min(p.compute_bound, p.io_bound)

                    # ****************************** ENFORCE OBJ-INDEPENDENT CONSTRAINTS ******************************
                    if(p.core_count < 1 or p.l3_count < 1 or p.mc_count < 1 or p.io_count < 1):
                        infs_handler(result, "must have at least one of each component")
                    
                    if(p.core_freq < p.core_freq_min or p.core_freq > p.core_freq_absolute_max):
                        infs_handler(result, "core_freq out of range")
                    
                    if(p.P_max < p.P_die):
                        infs_handler(result, "P_max < P_die")
                    
                    if(p.A_die < (p.bump_pitch**2) * (p.power_bump_count + p.mc_bump_count * p.mc_count + p.io_bump_count * p.io_count)):
                        infs_handler(result, "bump constraint not met")
                    
                    if(p.max_wire < p.mc_count * p.wires_per_mc):
                        infs_handler(result, "wire constraint not met")
                    
                    # Sanity Check: no param/var in the model should be negative
                    for key, value in p.__dict__.items():
                        if(value < 0):
                            infs_handler(result, f'{key} has negative value of {value}')
                    
                    # ****************************** ENFORCE OBJ-DEPENDENT CONSTRAINTS ******************************
                    if(obj == "max_perf"):
                        if(p.areaUB < p.A_die):
                            infs_handler(result, f'areaUB < A_die')
                        if(p.powerUB < p.P_die):
                            infs_handler(result, f'powerUB < P_die')
                        result["obj value"] = p.perf

                    elif(obj == "min_area"):
                        if(p.perf < p.perfLB):
                            infs_handler(result, f'perf < perfLB')
                        if(p.powerUB < p.P_die):
                            infs_handler(result, f'powerUB < P_die')
                        result["obj value"] = p.A_die

                    elif(obj == "min_power"):
                        if(p.areaUB < p.A_die):
                            infs_handler(result, f'areaUB < A_die')
                        if(p.perf < p.perfLB):
                            infs_handler(result, f'perf < perfLB')
                        result["obj value"] = p.P_die

                    # ***********************************************************************************************
                    
                    result["perf"] = p.perf
                    result["A_die"] = p.A_die
                    result["P_die"] = p.P_die
                    result["core_freq"] = p.core_freq

                    # Dump the entire namespace with all model param/variables
                    result["dump"] = copy.deepcopy(p.__dict__)
                    results.append(result)

    return results

def infs_handler(result, err):
    result["feasible"] = False
    result["err"] = err

    print(f'Infeasible: obj = {result["obj"]} | design point = {result["design point"]} | err = {result["err"]}')

def display(results, dump):
    for result in results:
        display_entry(result, dump)

def display_entry(result, dump):
    print('______________________________________________________')
    for key, value in result.items():
        if(key == "dump" and dump == False):
            continue
        elif(key == "dump" and dump == True):
            #print(json.dumps(value, sort_keys=True, indent=4))
            display_dump(value)
        elif(key == "feasible"):
            if(value == True):
                print(f'{bcolors.OKGREEN}{key} = {value}{bcolors.ENDC}')
            else:
                print(f'{bcolors.FAIL}{key} = {value}{bcolors.ENDC}')
        else:
            if type(value) == int or type(value) == float:
                if(value < 0.001 or value > 1000):
                    print(f'{key} = {sn_format(value)}')
                else:
                    print(f'{key} = {value}')
            else:
                print(f'{key} = {value}')

def display_dump(dump_dict):
    print(f'{{')
    for key, value in dump_dict.items():
        if(value < 0.001 or value > 1000):
            print(f'\t{key} = {sn_format(value)}')
        else:
            print(f'\t{key} = {value}')

    print(f'}}')

def infs_filter(results):

    # Only consider feasible design points
    filtered = copy.deepcopy(results)
    filtered = [result for result in filtered if result["feasible"] == True]
    return filtered, len(results) - len(filtered)

def find_best(results, obj, dump):
    print('######################################################')

    print('List of objective values:')
    obj_vals = []
    design_points = []
    for result in results:
        obj_vals.append(result["obj value"])
        design_points.append(result["design point"])

    for i in range(len(obj_vals)):
        if(obj_vals[i] < 0.001 or obj_vals[i] > 1000):
            print(f'{i + 1}. {design_points[i]}: {sn_format(obj_vals[i])}')
        else:
            print(f'{i + 1}. {design_points[i]}: {obj_vals[i]}')

    print('\nBest design point:')
    if "max" in obj:
        max_value = max(obj_vals)
        max_index = obj_vals.index(max_value)
        display_entry(results[max_index], dump)

    elif "min" in obj:
        min_value = min(obj_vals)
        min_index = obj_vals.index(min_value)
        display_entry(results[min_index], dump)

# Use two different x-axis in case the sets of feasible design points are different
def double_line_plot(x1, x2, y1, y2, y1_label, y2_label, x_axis_label, y_axis_label, title):
    plt.figure(figsize=(12, 8))
    plt.plot(x1, y1, **{'color': 'blue', 'marker': 'o'}, label=y1_label, linestyle='-')
    plt.plot(x2, y2, **{'color': 'red', 'marker': 'o'}, label=y2_label, linestyle='--')

    plt.title(title, fontweight ='bold', fontsize = 15)
    plt.xlabel(x_axis_label, fontweight ='bold', fontsize = 15)
    plt.ylabel(y_axis_label, fontweight ='bold', fontsize = 15)
    plt.legend()

    plt.savefig(f'results/{title}.pdf')
    plt.close()

def multi_line_plot(x1, x2, x3, x4, x5, x6, y1, y2, y3, y4, y5, y6, y1_label, y2_label, y3_label, y4_label, y5_label, y6_label, x_axis_label, y_axis_label, title):
    plt.figure(figsize=(12, 8))
    plt.plot(x1, y1, **{'color': 'blue', 'marker': 'o'}, label=y1_label, linestyle='-')
    plt.plot(x2, y2, **{'color': 'purple', 'marker': 'o'}, label=y2_label, linestyle='-')
    plt.plot(x3, y3, **{'color': 'yellow', 'marker': 'o'}, label=y3_label, linestyle='-')
    plt.plot(x4, y4, **{'color': 'grey', 'marker': 'o'}, label=y4_label, linestyle='-', linewidth=10)
    plt.plot(x5, y5, **{'color': 'orange', 'marker': 'o'}, label=y5_label, linestyle='-')
    plt.plot(x6, y6, **{'color': 'red', 'marker': 'o'}, label=y6_label, linestyle='--')

    plt.title(title, fontweight ='bold', fontsize = 15)
    plt.xlabel(x_axis_label, fontweight ='bold', fontsize = 15)
    plt.ylabel(y_axis_label, fontweight ='bold', fontsize = 15)
    plt.legend()

    plt.savefig(f'results/{title}.pdf')
    plt.close()

def plot(results):

    with open("app_props.json", 'r') as fp:
        app_props = json.load(fp)

    for app_prop in app_props:

        ddrs = []
        for i in range(5): # MANUAL
            ddrs.append({"x": [], "perf": [], "l3_bound": [], "mc_bound": [], "compute_bound": [], "io_bound": [], })

        # filter all results into the set of result with specific app profile
        curr = [result for result in results if result["app_prop"]["ai_app"] == app_prop["ai_app"]]
        curr = [result for result in curr if result["app_prop"]["workset_size"] == app_prop["workset_size"]]

        hbm_x = []
        hbm_perf = []
        hbm_l3_bound = []
        hbm_mc_bound = []
        hbm_compute_bound = []
        hbm_io_bound = []

        ddr0 = [result for result in curr if result["mem"]["name"] == "DDR4-3200 theta_ca=0.26904"]
        ddr1 = [result for result in curr if result["mem"]["name"] == "DDR5-4000 theta_ca=0.22732"]
        ddr2 = [result for result in curr if result["mem"]["name"] == "DDR5-4800 theta_ca=0.18146"]
        ddr3 = [result for result in curr if result["mem"]["name"] == "DDR5-6400 theta_ca=0.0975"]
        ddr4 = [result for result in curr if result["mem"]["name"] == "DDR5-6400 theta_ca=0.09501"]
        hbm = [result for result in curr if result["mem"]["name"] == "HBM2 theta_ca=0.32552"]
        ai_app = app_prop["ai_app"]
        workset_size = app_prop["workset_size"] / 1E6
        arithmetic_intensity = curr[0]['dump']['arithmetic_intensity']

        for result in ddr0:
            ddrs[0]["x"].append(result['dump']['l3_count'])
            ddrs[0]["perf"].append(result['dump']['perf'])
            ddrs[0]["l3_bound"].append(result['dump']['l3_bound'])
            ddrs[0]["mc_bound"].append(result['dump']['mc_bound'])
            ddrs[0]["compute_bound"].append(result['dump']['compute_bound'])
            ddrs[0]["io_bound"].append(result['dump']['io_bound'])

        for result in ddr1:
            ddrs[1]["x"].append(result['dump']['l3_count'])
            ddrs[1]["perf"].append(result['dump']['perf'])
            ddrs[1]["l3_bound"].append(result['dump']['l3_bound'])
            ddrs[1]["mc_bound"].append(result['dump']['mc_bound'])
            ddrs[1]["compute_bound"].append(result['dump']['compute_bound'])
            ddrs[1]["io_bound"].append(result['dump']['io_bound'])

        for result in ddr2:
            ddrs[2]["x"].append(result['dump']['l3_count'])
            ddrs[2]["perf"].append(result['dump']['perf'])
            ddrs[2]["l3_bound"].append(result['dump']['l3_bound'])
            ddrs[2]["mc_bound"].append(result['dump']['mc_bound'])
            ddrs[2]["compute_bound"].append(result['dump']['compute_bound'])
            ddrs[2]["io_bound"].append(result['dump']['io_bound'])

        for result in ddr3:
            ddrs[3]["x"].append(result['dump']['l3_count'])
            ddrs[3]["perf"].append(result['dump']['perf'])
            ddrs[3]["l3_bound"].append(result['dump']['l3_bound'])
            ddrs[3]["mc_bound"].append(result['dump']['mc_bound'])
            ddrs[3]["compute_bound"].append(result['dump']['compute_bound'])
            ddrs[3]["io_bound"].append(result['dump']['io_bound'])

        for result in ddr4:
            ddrs[4]["x"].append(result['dump']['l3_count'])
            ddrs[4]["perf"].append(result['dump']['perf'])
            ddrs[4]["l3_bound"].append(result['dump']['l3_bound'])
            ddrs[4]["mc_bound"].append(result['dump']['mc_bound'])
            ddrs[4]["compute_bound"].append(result['dump']['compute_bound'])
            ddrs[4]["io_bound"].append(result['dump']['io_bound'])

        for result in hbm:
            hbm_x.append(result['dump']['l3_count'])
            hbm_perf.append(result['dump']['perf'])
            hbm_l3_bound.append(result['dump']['l3_bound'])
            hbm_mc_bound.append(result['dump']['mc_bound'])
            hbm_compute_bound.append(result['dump']['compute_bound'])
            hbm_io_bound.append(result['dump']['io_bound'])

        for i in range(len(ddrs)):
            ddrs[i]["perf"] = np.array(ddrs[i]["perf"]) / 1E9
            ddrs[i]["l3_bound"] = np.array(ddrs[i]["l3_bound"]) / 1E9
            ddrs[i]["mc_bound"] = np.array(ddrs[i]["mc_bound"]) / 1E9
            ddrs[i]["compute_bound"] = np.array(ddrs[i]["compute_bound"]) / 1E9
            ddrs[i]["io_bound"] = np.array(ddrs[i]["io_bound"]) / 1E9

        hbm_perf = np.array(hbm_perf) / 1E9
        hbm_l3_bound = np.array(hbm_l3_bound) / 1E9
        hbm_mc_bound = np.array(hbm_mc_bound) / 1E9
        hbm_compute_bound = np.array(hbm_compute_bound) / 1E9
        hbm_io_bound = np.array(hbm_io_bound) / 1E9


        multi_line_plot(x1=ddrs[0]["x"], x2=ddrs[1]["x"], x3=ddrs[2]["x"], x4=ddrs[3]["x"], x5=ddrs[4]["x"], x6=hbm_x, 
                        y1=ddrs[0]["perf"], y2=ddrs[1]["perf"], y3=ddrs[2]["perf"], y4=ddrs[3]["perf"], y5=ddrs[4]["perf"], y6=hbm_perf, 
                        y1_label='DDR4-3200 theta_ca=0.26904', y2_label='DDR5-4000 theta_ca=0.22732', y3_label='DDR5-4800 theta_ca=0.18146', y4_label='DDR5-6400 theta_ca=0.0975', y5_label='DDR5-6400 theta_ca=0.09501', y6_label='HBM2 theta_ca=0.32552',
                        x_axis_label='Number of L3 Slices', y_axis_label='Performance (Gflop/s)',
                        title=f'[{ai_app} App. AI, {"{:.4f}".format(arithmetic_intensity)} Eff. AI, {workset_size} MB Workset] DDR vs HBM Performance')
        
        double_line_plot(x1=ddrs[0]["x"], x2=ddrs[0]["x"], y1=ddrs[0]["compute_bound"], y2=ddrs[0]["io_bound"], 
                        y1_label='Compute Throughput', y2_label='Memory Bandwidth',
                        x_axis_label='Number of L3 Slices', y_axis_label='',
                        title=f'[{ai_app} App. AI, {"{:.4f}".format(arithmetic_intensity)} Eff. AI, {workset_size} MB Workset] DDR4-3200 Compute vs IO Bound')

        double_line_plot(x1=ddrs[0]["x"], x2=ddrs[0]["x"], y1=ddrs[0]["l3_bound"], y2=ddrs[0]["mc_bound"], 
                        y1_label='L3 Effective BW', y2_label='MC Effective BW',
                        x_axis_label='Number of L3 Slices', y_axis_label='',
                        title=f'[{ai_app} App. AI, {"{:.4f}".format(arithmetic_intensity)} Eff. AI, {workset_size} MB Workset] DDR4-3200 L3 vs MC Bound')

        double_line_plot(x1=ddrs[2]["x"], x2=ddrs[2]["x"], y1=ddrs[2]["compute_bound"], y2=ddrs[2]["io_bound"], 
                        y1_label='Compute Throughput', y2_label='Memory Bandwidth',
                        x_axis_label='Number of L3 Slices', y_axis_label='',
                        title=f'[{ai_app} App. AI, {"{:.4f}".format(arithmetic_intensity)} Eff. AI, {workset_size} MB Workset] DDR5-4800 Compute vs IO Bound')

        double_line_plot(x1=ddrs[2]["x"], x2=ddrs[2]["x"], y1=ddrs[2]["l3_bound"], y2=ddrs[2]["mc_bound"], 
                        y1_label='L3 Effective BW', y2_label='MC Effective BW',
                        x_axis_label='Number of L3 Slices', y_axis_label='',
                        title=f'[{ai_app} App. AI, {"{:.4f}".format(arithmetic_intensity)} Eff. AI, {workset_size} MB Workset] DDR5-4800 L3 vs MC Bound')

        double_line_plot(x1=hbm_x, x2=hbm_x, y1=hbm_compute_bound, y2=hbm_io_bound, 
                        y1_label='Compute Throughput', y2_label='Memory Bandwidth',
                        x_axis_label='Number of L3 Slices', y_axis_label='',
                        title=f'[{ai_app} App. AI, {"{:.4f}".format(arithmetic_intensity)} Eff. AI, {workset_size} MB Workset] HBM Compute vs IO Bound')

        double_line_plot(x1=hbm_x, x2=hbm_x, y1=hbm_l3_bound, y2=hbm_mc_bound, 
                        y1_label='L3 Effective BW', y2_label='MC Effective BW',
                        x_axis_label='Number of L3 Slices', y_axis_label='',
                        title=f'[{ai_app} App. AI, {"{:.4f}".format(arithmetic_intensity)} Eff. AI, {workset_size} MB Workset] HBM L3 vs MC Bound')

def sn_format(value):
    return "{:.4e}".format(value)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    # use -o flag to specify max_perf, min_area, or min_power objective
    parser.add_argument("-o", "--objective", dest = "obj")

    # use -perf -area -power flags to override default values for perf, area, and power limit
    parser.add_argument("-perf", dest = "perfLB", type=float, default="10")
    parser.add_argument("-area", dest = "areaUB", type=float, default="1000")
    parser.add_argument("-power", dest = "powerUB", type=float, default="287.5")

    # use -display flag to view key information about each design point
    # o.w. only print best design point
    parser.add_argument("-display", action='store_true')

    # use -dump flag to view complete information about any design point displayed
    parser.add_argument("-dump", action='store_true')
    args = parser.parse_args()
    
    load_data()
    results = solve(args.obj, args.perfLB, args.areaUB, args.powerUB)
    filtered, infs_count = infs_filter(results)

    if(args.display == True):
        display(results, args.dump)
    
    find_best(filtered, args.obj, args.dump)
    plot(filtered)

    print('######################################################')
    print(f'{len(results)} design points evaluated.')
    if(infs_count == 0):
        print(f'{bcolors.OKGREEN}{infs_count} infeasible design points removed.{bcolors.ENDC}')
    else:
        print(f'{bcolors.FAIL}{infs_count} infeasible design points removed.{bcolors.ENDC}')

