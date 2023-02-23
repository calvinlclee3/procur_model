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

def set_default():

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
    default["mem_freq"] = 4300E6
    default["mc_power_ctrl"] = 3                             # per MC

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

    # # objective-dependent constraints
    # default["PerfLB"] = 10E9
    # default["PerfUB"] = 0
    # default["AreaLB"] = 0
    # # 1000E-6
    # default["AreaUB"] = 1000E-6
    # default["PowerLB"] = 0
    # # P_max: 287.5
    # default["PowerUB"] = 287.5

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
    core = []
    core.append({})
    core[0]['name'] = "Intel Core i9-13900K"
    core[0]['core_freq'] = 3E9
    core[0]['core_count'] = 24
    core[0]['core_area'] = 7E-6
    core[0]['die_voltage_nominal'] = 1.2
    core[0]['l1_capacity'] = 80E3
    core[0]['l2_capacity'] = 2E6
    # core.append({})
    # core[1]['name'] = "Intel Core i9-13900K"
    # core[1]['core_freq'] = 3E9
    # core[1]['core_count'] = 12
    # core[1]['core_area'] = 4E-6
    # core[1]['die_voltage_nominal'] = 1.0
    # core.append({})
    # core[2]['name'] = "Intel Core i3-12100F"
    # core[2]['core_freq'] = 3.3E9
    # core[2]['core_count'] = 2
    # core[2]['core_area'] = 9E-6
    # core[2]['die_voltage_nominal'] = 1.4

    with open("core.json", "w") as outfile:
        json.dump(core, outfile)

    mem = []
    mem.append({})
    mem[0]['name'] = "DDR4-3200"
    mem[0]['mc_bw'] = 25.6E9
    mem[0]['mc_count'] = 2
    mem[0]['mc_area'] = 10E-6
    mem[0]['mem_freq'] = 1600E6
    mem[0]['energy_per_wire'] = 15E-12
    mem[0]['bump_pitch'] = 100E-6
    mem[0]['current_per_bump'] = 520.8333333E-3
    mem[0]['l3_bw'] = 20E9
    mem[0]['T_j_max'] = 110
    mem[0]['ai_app'] = 25
    mem[0]["workset_size"] = 50E6
    

    mem.append({})
    mem[1]['name'] = "HBM2"
    mem[1]['mc_bw'] = 16E9
    mem[1]['mc_count'] = 16
    mem[1]['mc_area'] = 10E-6
    mem[1]['mem_freq'] = 2000E6
    mem[1]['energy_per_wire'] = 3E-12
    mem[1]['bump_pitch'] = 40E-6
    mem[1]['current_per_bump'] = 83.3333333E-3
    mem[1]['l3_bw'] = 20E9
    mem[1]['T_j_max'] = 110
    mem[1]['ai_app'] = 25
    mem[1]["workset_size"] = 50E6

    # mem.append({})
    # mem[2]['name'] = "HBM3"
    # mem[2]['mc_bw'] = 1024*6000E6/8
    # mem[2]['mc_count'] = 4
    # mem[2]['mc_area'] = 3E-6
    # mem[2]['mem_freq'] = 6000E6

    with open("mem.json", "w") as outfile:
        json.dump(mem, outfile)

    l3_config = []
    for i in range(1, 51):
        l3_config.append({"name": f"{i}x L3s", "l3_count":i})
    
    with open("l3_config.json", "w") as outfile:
        json.dump(l3_config, outfile)
    


    


def solve(obj, perfLB, areaUB, powerUB):

    results = []

    print(f'Solving for objective {obj} with perfLB={perfLB} Gflop/s, areaUB={areaUB} mm2, powerUB={powerUB} W\n')
    
    with open("default.json", 'r') as fp:
        default = json.load(fp)

    with open("core.json", 'r') as fp:
        cores = json.load(fp)

    with open("mem.json", 'r') as fp:
        mems = json.load(fp)

    with open("l3_config.json", 'r') as fp:
        l3_configs = json.load(fp)

    for l3_config in l3_configs:
        for mem in mems:
            for core in cores:
                result = {}
                result["design point"] = [core["name"], mem["name"], l3_config["name"]]
                result["obj"] = obj
                result["core"] = copy.deepcopy(core)
                result["mem"] = copy.deepcopy(mem)
                result["l3_config"] = copy.deepcopy(l3_config)
                result["feasible"] = True

                # Overwrite default values, but only for keys that are already in default.json
                default.update((k, mem[k]) for k in default.keys() & mem.keys())
                default.update((k, core[k]) for k in default.keys() & core.keys())
                default.update((k, l3_config[k]) for k in default.keys() & l3_config.keys())

                # Convert dict to namespace for readability
                p = SimpleNamespace(**default)

                # Set objective-dependent constraints from CLI
                p.perfLB = perfLB * 1E9 
                p.areaUB = areaUB * 1E-6 
                p.powerUB = powerUB 

                # ****************************** MODEL EQUATIONS ******************************

                # Compute max power allowed by thermal constraint.
                p.theta_ja = (p.theta_jc + p.theta_ca)*(p.theta_jb + p.theta_ba)/(p.theta_jc + p.theta_ca + p.theta_jb + p.theta_ba);
                p.delta_T = p.T_j_max - p.T_ambient
                p.P_max = p.delta_T / p.theta_ja

                # Compute power of a memory controller.
                p.mc_power_phys = p.energy_per_wire * p.mem_freq * p.wires_per_mc
                p.mc_power = p.mc_power_phys + p.mc_power_ctrl

                # Compute arithmetic intensity.
                p.arithmetic_intensity = (p.l1_capacity + p.l2_capacity) / p.workset_size * p.ai_app

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
                    print(f'{key} = {"{:.4e}".format(value)}')
                else:
                    print(f'{key} = {value}')
            else:
                print(f'{key} = {value}')

def display_dump(dump_dict):
    print(f'{{')
    for key, value in dump_dict.items():
        if(value < 0.001 or value > 1000):
            print(f'\t{key} = {"{:.4e}".format(value)}')
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
            print(f'{i + 1}. {design_points[i]}: {"{:.4e}".format(obj_vals[i])}')
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

def plot(results):

    ddr_x = []
    ddr_perf = []
    ddr_l3_bound = []
    ddr_mc_bound = []
    ddr_compute_bound = []
    ddr_io_bound = []

    hbm_x = []
    hbm_perf = []
    hbm_l3_bound = []
    hbm_mc_bound = []
    hbm_compute_bound = []
    hbm_io_bound = []


    ddr = [result for result in results if result["mem"]["name"] == "DDR4-3200"]
    hbm = [result for result in results if result["mem"]["name"] == "HBM2"]
    ai_app = results[0]['dump']['ai_app']
    arithmetic_intensity = results[0]['dump']['arithmetic_intensity']
    workset_size = results[0]['dump']['workset_size'] / 1E6 

    for result in ddr:
        ddr_x.append(result['l3_config']['l3_count'])
        ddr_perf.append(result['perf'])
        ddr_l3_bound.append(result['dump']['l3_bound'])
        ddr_mc_bound.append(result['dump']['mc_bound'])
        ddr_compute_bound.append(result['dump']['compute_bound'])
        ddr_io_bound.append(result['dump']['io_bound'])

    for result in hbm:
        hbm_x.append(result['l3_config']['l3_count'])
        hbm_perf.append(result['perf'])
        hbm_l3_bound.append(result['dump']['l3_bound'])
        hbm_mc_bound.append(result['dump']['mc_bound'])
        hbm_compute_bound.append(result['dump']['compute_bound'])
        hbm_io_bound.append(result['dump']['io_bound'])

    ddr_perf = np.array(ddr_perf) / 1E9
    ddr_l3_bound = np.array(ddr_l3_bound) / 1E9
    ddr_mc_bound = np.array(ddr_mc_bound) / 1E9
    ddr_compute_bound = np.array(ddr_compute_bound) / 1E9
    ddr_io_bound = np.array(ddr_io_bound) / 1E9

    hbm_perf = np.array(hbm_perf) / 1E9
    hbm_l3_bound = np.array(hbm_l3_bound) / 1E9
    hbm_mc_bound = np.array(hbm_mc_bound) / 1E9
    hbm_compute_bound = np.array(hbm_compute_bound) / 1E9
    hbm_io_bound = np.array(hbm_io_bound) / 1E9


    double_line_plot(x1=ddr_x, x2=hbm_x, y1=ddr_perf, y2=hbm_perf, 
                     y1_label='DDR4-3200', y2_label='HBM2',
                     x_axis_label='Number of L3 Slices', y_axis_label='Performance (Gflop/s)',
                     title=f'DDR vs HBM Performance @ {ai_app} App. AI, {arithmetic_intensity} Eff. AI, {workset_size} MB Workset Size')
    
    double_line_plot(x1=ddr_x, x2=ddr_x, y1=ddr_compute_bound, y2=ddr_io_bound, 
                     y1_label='Compute Throughput', y2_label='Memory Bandwidth',
                     x_axis_label='Number of L3 Slices', y_axis_label='',
                     title=f'DDR Compute vs IO Bound @ {ai_app} App. AI, {arithmetic_intensity} Eff. AI, {workset_size} MB Workset Size')

    double_line_plot(x1=ddr_x, x2=ddr_x, y1=ddr_l3_bound, y2=ddr_mc_bound, 
                     y1_label='L3 Effective BW', y2_label='MC Effective BW',
                     x_axis_label='Number of L3 Slices', y_axis_label='',
                     title=f'DDR L3 vs MC @ {ai_app} App. AI, {arithmetic_intensity} Eff. AI, {workset_size} MB Workset Size')

    double_line_plot(x1=hbm_x, x2=hbm_x, y1=hbm_compute_bound, y2=hbm_io_bound, 
                     y1_label='Compute Throughput', y2_label='Memory Bandwidth',
                     x_axis_label='Number of L3 Slices', y_axis_label='',
                     title=f'HBM Compute vs IO Bound @ {ai_app} App. AI, {arithmetic_intensity} Eff. AI, {workset_size} MB Workset Size')

    double_line_plot(x1=hbm_x, x2=hbm_x, y1=hbm_l3_bound, y2=hbm_mc_bound, 
                     y1_label='L3 Effective BW', y2_label='MC Effective BW',
                     x_axis_label='Number of L3 Slices', y_axis_label='',
                     title=f'HBM L3 vs MC @ {ai_app} App. AI, {arithmetic_intensity} Eff. AI, {workset_size} MB Workset Size')

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    # use -o flag to specify max_perf, min_area, or min_power objective
    parser.add_argument("-o", "--objective", dest = "obj")

    # use -perf -area -power flags to override default values for perf, area, and power limit
    parser.add_argument("-perf", dest = "perfLB", type=float, default="10")
    parser.add_argument("-area", dest = "areaUB", type=float, default="1000")
    parser.add_argument("-power", dest = "powerUB", type=float, default="287.5")

    # use -dump flag to view the dump of all parameters
    parser.add_argument("-dump", action='store_true')
    args = parser.parse_args()
    
    set_default()
    results = solve(args.obj, args.perfLB, args.areaUB, args.powerUB)
    filtered, infs_count = infs_filter(results)

    display(results, args.dump)
    find_best(filtered, args.obj, args.dump)
    plot(filtered)

    print('######################################################')
    if(infs_count == 0):
        print(f'{bcolors.OKGREEN}{infs_count} infeasible design points removed.{bcolors.ENDC}')
    else:
        print(f'{bcolors.FAIL}{infs_count} infeasible design points removed.{bcolors.ENDC}')

