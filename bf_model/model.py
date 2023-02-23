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


def write_json():

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
    default["core_area"] = 10E-6 
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

    # IMPORTANT: What used to be variables in AMPL

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
    core[0]['name'] = "Intel Core i7-12700K"
    core[0]['core_freq'] = 3.6E9
    core[0]['core_count'] = 6
    core[0]['core_area'] = 10E-6
    core[0]['die_voltage_nominal'] = 1.2
    core.append({})
    core[1]['name'] = "Intel Core i9-13900K"
    core[1]['core_freq'] = 3E9
    core[1]['core_count'] = 12
    core[1]['core_area'] = 7E-6
    core[1]['die_voltage_nominal'] = 1.0
    core.append({})
    core[2]['name'] = "Intel Core i3-12100F"
    core[2]['core_freq'] = 3.3E9
    core[2]['core_count'] = 2
    core[2]['core_area'] = 12E-6
    core[2]['die_voltage_nominal'] = 1.4

    with open("core.json", "w") as outfile:
        json.dump(core, outfile)

    mem = []
    mem.append({})
    mem[0]['name'] = "Dual Channel DDR4"
    mem[0]['mc_bw'] = 72*3200E6/8
    mem[0]['mc_count'] = 2
    mem[0]['mc_area'] = 5E-6
    mem[0]['mem_freq'] = 3200E6
    mem.append({})
    mem[1]['name'] = "Dual Channel DDR5"
    mem[1]['mc_bw'] = 64*4800E6/8
    mem[1]['mc_count'] = 2
    mem[1]['mc_area'] = 7E-6
    mem[1]['mem_freq'] = 4800E6
    mem.append({})
    mem[2]['name'] = "HBM3"
    mem[2]['mc_bw'] = 1024*6000E6/8
    mem[2]['mc_count'] = 4
    mem[2]['mc_area'] = 3E-6
    mem[2]['mem_freq'] = 6000E6

    with open("mem.json", "w") as outfile:
        json.dump(mem, outfile)
    


    


def solve(obj, perfLB, areaUB, powerUB):

    results = []

    print(f'Solving for objective {obj} with perfLB={perfLB}, areaUB={areaUB}, powerUB={powerUB}\n')
    
    with open("default.json", 'r') as fp:
        default = json.load(fp)

    with open("core.json", 'r') as fp:
        cores = json.load(fp)

    with open("mem.json", 'r') as fp:
        mems = json.load(fp)
    
    for core in cores:
        for mem in mems:

            result = {}
            result["design point"] = [core["name"], mem["name"]]
            result["obj"] = obj
            result["core"] = copy.deepcopy(core)
            result["mem"] = copy.deepcopy(mem)
            result["feasible"] = True

            # Overwrite default values, but only for keys that are already in default.json
            default.update((k, mem[k]) for k in default.keys() & mem.keys())
            default.update((k, core[k]) for k in default.keys() & core.keys())

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

            # 5% increase in core_freq_max -> 10% increase in core_area
            if(p.core_freq < p.core_freq_base_max):
                p.core_area_multiplier = 1
            else:
                p.core_area_multiplier = (p.core_freq/p.core_freq_base_max - 1)*2 + 1

            # die_voltage scales linearly with core_freq
            p.die_voltage = (p.core_freq / p.core_freq_nominal) * p.die_voltage_nominal
            
            p.core_power = p.core_freq * p.capacitance_per_core * (p.die_voltage**2)

            p.P_die  = p.core_count * p.core_power + p.io_count * p.io_power
            p.P_die += p.l3_count   * p.l3_power   + p.mc_count * p.mc_power

            p.A_die  = p.core_count * p.core_area * p.core_area_multiplier
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


def findBest(results, obj, dump):
    print('######################################################')

    # Only consider feasible design points
    filtered = [result for result in results if result["feasible"] == True]

    print('List of objective values:')
    obj_vals = []
    design_points = []
    for result in filtered:
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
        display_entry(filtered[max_index], dump)

    elif "min" in obj:
        min_value = min(obj_vals)
        min_index = obj_vals.index(min_value)
        display_entry(filtered[min_index], dump)



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
    
    write_json()
    results = solve(args.obj, args.perfLB, args.areaUB, args.powerUB)
    display(results, args.dump)
    findBest(results, args.obj, args.dump)

