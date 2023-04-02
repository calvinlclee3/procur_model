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
    default["l1_area"] = 1.064614421E-6
    default["l2_area"] = 4.282729752E-6
    default["l3_area"] = 4E-6
    default["mc_area"] = 10E-6
    default["io_area"] = 20E-6

    # power of each component
    default["l3_power"] = 0.2
    default["io_power"] = 10

    # bump parameters
    default["bump_pitch_die"] = 150E-6
    default["die_voltage_nominal"] = 1.2
    default["current_per_bump_die"] = 520.8333333E-3
    default["mc_bump_count"] = 160
    default["io_bump_count"] = 114

    # wire parameters
    default["package_layer"] = 6
    default["link_pitch"] = 25E-6

    # memory controller parameters
    default["wires_per_mc"] = 160
    default["energy_per_wire"] = 15E-12
    default["mc_freq"] = 1600E6
    default["mc_freq_nominal"] = 1600E6
    default["mc_voltage_nominal"] = 1.2
    default["mc_power_ctrl_nominal"] = 3                     # per MC

    # performance parameters
    default["ai_app"] = 100                                  # operations / byte
    default["IPC"] = 3.175                                   # instructions / cycle
    default["capacitance_per_core"] = 2.96080965E-9          # for the core only, per core
    default["l1_capacity"] = 64E3                            # per L1 (L1 is part of the core)
    default["l2_capacity"] = 1E6                             # per L2 (L2 is part of the core)
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
    default["wafer_cost_die"] = 6000
    default["wafer_cost_intp"] = 2500
    default["wafer_dia_die"] = 300E-3
    default["wafer_dia_intp"] = 300E-3
    default["defect_density_die"] = 0.001E6
    default["defect_density_intp"] = 0.0003E6
    default["clustering_factor_die"] = 2
    default["clustering_factor_intp"] = 2
    default["mem_cost_per_mc"] = 41.99                       # Default always overwritten.
    default["use_intp"] = 0                                  # 0 for False, 1 for True. Default always overwritten.
    default["bump_pitch_intp"] = 150E-6
    default["HBM_area_per_mc"] = 100E-6     
    default["HBM_power_per_mc"] = 8.13056
    default["intp_asm_cost"] = 10
    default["pkg_cost_per_sqmm"] = 0.02E6
    default["bump_pitch_pkg"] = 900E-6
    default["pkg_non_io_area"] = 0E-6
    default["current_per_bump_pkg"] = 250E-3

    # IMPORTANT: What used to be variables in the optimization model

    # number of each component (integer)
    default["core_count"] = 12
    default["l3_count"] = 12.5
    default["mc_count"] = 2
    default["io_count"] = 1

    default["core_freq"] = 3.6E9

    with open("default.json", "w") as outfile:
        json.dump(default, outfile)

    # ****************************** WRITING CPU ARCH VALUES ******************************

    cores = []
    cores.append({})
    cores[0]['name'] = "Intel Xeon Platinum 8380"
    cores[0]['core_count'] = 40
    cores[0]['core_freq'] = 2.85E9
    cores[0]['die_voltage_nominal'] = 1.2
    cores[0]["l1_area"] = 1.064614421E-6
    cores[0]["l2_area"] = 4.282729752E-6
    cores[0]["l3_area"] = 4E-6
    cores[0]["l1_capacity"] = 64E3                     
    cores[0]["l2_capacity"] = 1E6                          
    cores[0]["l3_capacity"] = 2E6                          

    with open("cores.json", "w") as outfile:
        json.dump(cores, outfile)

    mems = []
    mems.append({})
    mems[0]['name'] = "DDR4-2400 4Ch theta_ca=0.18561"
    mems[0]['mc_bw'] = 1200E6 * 2 * 8
    mems[0]['mc_count'] = 4
    mems[0]['mc_area'] = 10E-6
    mems[0]['mc_freq'] = 1200E6
    mems[0]['energy_per_wire'] = 15E-12
    mems[0]['bump_pitch_die'] = 150E-6
    mems[0]['current_per_bump_die'] = 520.8333333E-3
    mems[0]['mc_bump_count'] = 160
    mems[0]['wires_per_mc'] = 160
    mems[0]['theta_ca'] = 0.18561
    mems[0]["use_intp"] = 0
    mems[0]['mem_cost_per_mc'] = 41.99
    mems[0]['l3_bw'] = 30E9
    mems[0]['T_j_max'] = 110

    mems.append({})
    mems[1]['name'] = "DDR4-2400 6Ch theta_ca=0.17837"
    mems[1]['mc_bw'] = 1200E6 * 2 * 8
    mems[1]['mc_count'] = 6
    mems[1]['mc_area'] = 10E-6
    mems[1]['mc_freq'] = 1200E6
    mems[1]['energy_per_wire'] = 15E-12
    mems[1]['bump_pitch_die'] = 150E-6
    mems[1]['current_per_bump_die'] = 520.8333333E-3
    mems[1]['mc_bump_count'] = 160
    mems[1]['wires_per_mc'] = 160
    mems[1]['theta_ca'] = 0.17837
    mems[1]["use_intp"] = 0
    mems[1]['mem_cost_per_mc'] = 41.99
    mems[1]['l3_bw'] = 30E9
    mems[1]['T_j_max'] = 110

    mems.append({})
    mems[2]['name'] = "DDR4-3200 4Ch theta_ca=0.17465"
    mems[2]['mc_bw'] = 1600E6 * 2 * 8
    mems[2]['mc_count'] = 4
    mems[2]['mc_area'] = 10E-6
    mems[2]['mc_freq'] = 1600E6
    mems[2]['energy_per_wire'] = 15E-12
    mems[2]['bump_pitch_die'] = 150E-6
    mems[2]['current_per_bump_die'] = 520.8333333E-3
    mems[2]['mc_bump_count'] = 160
    mems[2]['wires_per_mc'] = 160
    mems[2]['theta_ca'] = 0.17465
    mems[2]["use_intp"] = 0
    mems[2]['mem_cost_per_mc'] = 41.99
    mems[2]['l3_bw'] = 30E9
    mems[2]['T_j_max'] = 110

    mems.append({})
    mems[3]['name'] = "DDR4-3200 6Ch theta_ca=0.16302"
    mems[3]['mc_bw'] = 1600E6 * 2 * 8
    mems[3]['mc_count'] = 6
    mems[3]['mc_area'] = 10E-6
    mems[3]['mc_freq'] = 1600E6
    mems[3]['energy_per_wire'] = 15E-12
    mems[3]['bump_pitch_die'] = 150E-6
    mems[3]['current_per_bump_die'] = 520.8333333E-3
    mems[3]['mc_bump_count'] = 160
    mems[3]['wires_per_mc'] = 160
    mems[3]['theta_ca'] = 0.16302
    mems[3]["use_intp"] = 0
    mems[3]['mem_cost_per_mc'] = 41.99
    mems[3]['l3_bw'] = 30E9
    mems[3]['T_j_max'] = 110

    mems.append({})
    mems[4]['name'] = "DDR5-4800 4Ch theta_ca=0.1415"
    mems[4]['mc_bw'] = 2400E6 * 2 * 8
    mems[4]['mc_count'] = 4
    mems[4]['mc_area'] = 10E-6
    mems[4]['mc_freq'] = 2400E6
    mems[4]['energy_per_wire'] = 15E-12
    mems[4]['bump_pitch_die'] = 150E-6
    mems[4]['current_per_bump_die'] = 520.8333333E-3
    mems[4]['mc_bump_count'] = 160
    mems[4]['wires_per_mc'] = 160
    mems[4]['theta_ca'] = 0.1415     
    mems[4]["use_intp"] = 0
    mems[4]['mem_cost_per_mc'] = 52.99
    mems[4]['l3_bw'] = 30E9
    mems[4]['T_j_max'] = 110

    mems.append({})
    mems[5]['name'] = "DDR5-4800 6Ch theta_ca=0.1197"
    mems[5]['mc_bw'] = 2400E6 * 2 * 8
    mems[5]['mc_count'] = 6
    mems[5]['mc_area'] = 10E-6
    mems[5]['mc_freq'] = 2400E6
    mems[5]['energy_per_wire'] = 15E-12
    mems[5]['bump_pitch_die'] = 150E-6
    mems[5]['current_per_bump_die'] = 520.8333333E-3
    mems[5]['mc_bump_count'] = 160
    mems[5]['wires_per_mc'] = 160
    mems[5]['theta_ca'] = 0.1197
    mems[5]["use_intp"] = 0
    mems[5]['mem_cost_per_mc'] = 52.99
    mems[5]['l3_bw'] = 30E9
    mems[5]['T_j_max'] = 110

    mems.append({})
    mems[6]['name'] = "DDR5-5600 4Ch theta_ca=0.12389"
    mems[6]['mc_bw'] = 2800E6 * 2 * 8
    mems[6]['mc_count'] = 4
    mems[6]['mc_area'] = 10E-6
    mems[6]['mc_freq'] = 2800E6
    mems[6]['energy_per_wire'] = 15E-12
    mems[6]['bump_pitch_die'] = 150E-6
    mems[6]['current_per_bump_die'] = 520.8333333E-3
    mems[6]['mc_bump_count'] = 160
    mems[6]['wires_per_mc'] = 160
    mems[6]['theta_ca'] = 0.12389     # MIDLINE 0.12389
    mems[6]["use_intp"] = 0
    mems[6]['mem_cost_per_mc'] = 73.99
    mems[6]['l3_bw'] = 30E9
    mems[6]['T_j_max'] = 110

    mems.append({})
    mems[7]['name'] = "DDR5-5600 4Ch theta_ca=0.12052"
    mems[7]['mc_bw'] = 2800E6 * 2 * 8
    mems[7]['mc_count'] = 4
    mems[7]['mc_area'] = 10E-6
    mems[7]['mc_freq'] = 2800E6
    mems[7]['energy_per_wire'] = 15E-12
    mems[7]['bump_pitch_die'] = 150E-6
    mems[7]['current_per_bump_die'] = 520.8333333E-3
    mems[7]['mc_bump_count'] = 160
    mems[7]['wires_per_mc'] = 160
    mems[7]['theta_ca'] = 0.12052     
    mems[7]["use_intp"] = 0
    mems[7]['mem_cost_per_mc'] = 73.99
    mems[7]['l3_bw'] = 30E9
    mems[7]['T_j_max'] = 110

    mems.append({})
    mems[8]['name'] = "DDR5-5600 6Ch theta_ca=0.09446"
    mems[8]['mc_bw'] = 2800E6 * 2 * 8
    mems[8]['mc_count'] = 6
    mems[8]['mc_area'] = 10E-6
    mems[8]['mc_freq'] = 2800E6
    mems[8]['energy_per_wire'] = 15E-12
    mems[8]['bump_pitch_die'] = 150E-6
    mems[8]['current_per_bump_die'] = 520.8333333E-3
    mems[8]['mc_bump_count'] = 160
    mems[8]['wires_per_mc'] = 160
    mems[8]['theta_ca'] = 0.09446
    mems[8]["use_intp"] = 0
    mems[8]['mem_cost_per_mc'] = 73.99
    mems[8]['l3_bw'] = 30E9
    mems[8]['T_j_max'] = 110

    mems.append({})
    mems[9]['name'] = "HBM2 4Ch theta_ca=0.15934"
    mems[9]['mc_bw'] = 256E9
    mems[9]['mc_count'] = 4
    mems[9]['mc_area'] = 6.6831E-6
    mems[9]['mc_freq'] = 1000E6
    mems[9]['energy_per_wire'] = 3.5E-12
    mems[9]['bump_pitch_die'] = 50E-6
    mems[9]['current_per_bump_die'] = 57.87037E-3
    mems[9]['mc_bump_count'] = 1024
    mems[9]['wires_per_mc'] = 1024
    mems[9]['theta_ca'] = 0.15934
    mems[9]["use_intp"] = 1
    mems[9]['mem_cost_per_mc'] = 120
    mems[9]['l3_bw'] = 30E9
    mems[9]['T_j_max'] = 110

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

    # ****************************** WRITING GPU ARCH VALUES ******************************

    cores_gpu = []
    cores_gpu.append({})
    cores_gpu[0]['name'] = "TITAN V"
    cores_gpu[0]['core_count'] = 5120                  # spec
    cores_gpu[0]['core_freq'] = 1200E6                 # spec
    cores_gpu[0]['die_voltage_nominal'] = 1.2          # guessed
    cores_gpu[0]['core_area'] = 815E-6	* 0.56 / 5120    # total die area of 815 sqmm with ~56% dedicated to SM
                                                       # note the 56% number is from a different GPU (TU102)
    cores_gpu[0]["l1_area"] = 1.569843283E-6 / 64      # spec -> CACTI
    cores_gpu[0]["l2_area"] = 22.61591405E-6 / 5120    # spec -> CACTI
    cores_gpu[0]["l3_area"] = 4E-6                     # guessed, TITAN V only have L1/L2
    cores_gpu[0]["l1_capacity"] = 96E3 / 64            # spec (96kB per SM; 64 SPs per SM)         
    cores_gpu[0]["l2_capacity"] = 4.5E6 / 5120         # spec (4.5 MB Global L2; 5120 SPs in the entire GPU)              
    cores_gpu[0]["l3_capacity"] = 2E6                  # guessed, TITAN V only have L1/L2
    cores_gpu[0]["IPC"] = 12288E9 / 5120 / 1200E6      # worked backwards from FP32 flop rate (12288 GFLOPS)
    cores_gpu[0]["wafer_cost_die"] = 3984              # from CSET report for TSMC 12nm 300mm wafer (TITAN V is 12nm)
    cores_gpu[0]["core_freq_nominal"] = 1200E6         # scaling of die voltage from the correct baseline   
    cores_gpu[0]["core_freq_base_max"] = 1200E6        # scaling of core area from the correct baseline
    cores_gpu[0]["capacitance_per_core"] = 200 / 5120 / math.pow(1.2, 2) / 1200E6
                                                       # worked backwards from TDP
                                                       # much lower than CPU value

    with open("cores_gpu.json", "w") as outfile:
        json.dump(cores_gpu, outfile)

    mems_gpu = []
    mems_gpu.append({})
    mems_gpu[0]['name'] = "DDR4-2400 4Ch theta_ca=0.34046"
    mems_gpu[0]['mc_bw'] = 1200E6 * 2 * 8
    mems_gpu[0]['mc_count'] = 4
    mems_gpu[0]['mc_area'] = 10E-6
    mems_gpu[0]['mc_freq'] = 1200E6
    mems_gpu[0]['energy_per_wire'] = 15E-12
    mems_gpu[0]['bump_pitch_die'] = 150E-6
    mems_gpu[0]['current_per_bump_die'] = 520.8333333E-3
    mems_gpu[0]['mc_bump_count'] = 160
    mems_gpu[0]['wires_per_mc'] = 160
    mems_gpu[0]['theta_ca'] = 0.34046
    mems_gpu[0]["use_intp"] = 0
    mems_gpu[0]['mem_cost_per_mc'] = 41.99
    mems_gpu[0]['l3_bw'] = 30E9
    mems_gpu[0]['T_j_max'] = 110

    mems_gpu.append({})
    mems_gpu[1]['name'] = "DDR4-2400 6Ch theta_ca=0.32347"
    mems_gpu[1]['mc_bw'] = 1200E6 * 2 * 8
    mems_gpu[1]['mc_count'] = 6
    mems_gpu[1]['mc_area'] = 10E-6
    mems_gpu[1]['mc_freq'] = 1200E6
    mems_gpu[1]['energy_per_wire'] = 15E-12
    mems_gpu[1]['bump_pitch_die'] = 150E-6
    mems_gpu[1]['current_per_bump_die'] = 520.8333333E-3
    mems_gpu[1]['mc_bump_count'] = 160
    mems_gpu[1]['wires_per_mc'] = 160
    mems_gpu[1]['theta_ca'] = 0.32347
    mems_gpu[1]["use_intp"] = 0
    mems_gpu[1]['mem_cost_per_mc'] = 41.99
    mems_gpu[1]['l3_bw'] = 30E9
    mems_gpu[1]['T_j_max'] = 110

    mems_gpu.append({})
    mems_gpu[2]['name'] = "DDR4-3200 4Ch theta_ca=0.31491"
    mems_gpu[2]['mc_bw'] = 1600E6 * 2 * 8
    mems_gpu[2]['mc_count'] = 4
    mems_gpu[2]['mc_area'] = 10E-6
    mems_gpu[2]['mc_freq'] = 1600E6
    mems_gpu[2]['energy_per_wire'] = 15E-12
    mems_gpu[2]['bump_pitch_die'] = 150E-6
    mems_gpu[2]['current_per_bump_die'] = 520.8333333E-3
    mems_gpu[2]['mc_bump_count'] = 160
    mems_gpu[2]['wires_per_mc'] = 160
    mems_gpu[2]['theta_ca'] = 0.31491
    mems_gpu[2]["use_intp"] = 0
    mems_gpu[2]['mem_cost_per_mc'] = 41.99
    mems_gpu[2]['l3_bw'] = 30E9
    mems_gpu[2]['T_j_max'] = 110

    mems_gpu.append({})
    mems_gpu[3]['name'] = "DDR4-3200 6Ch theta_ca=0.28894"
    mems_gpu[3]['mc_bw'] = 1600E6 * 2 * 8
    mems_gpu[3]['mc_count'] = 6
    mems_gpu[3]['mc_area'] = 10E-6
    mems_gpu[3]['mc_freq'] = 1600E6
    mems_gpu[3]['energy_per_wire'] = 15E-12
    mems_gpu[3]['bump_pitch_die'] = 150E-6
    mems_gpu[3]['current_per_bump_die'] = 520.8333333E-3
    mems_gpu[3]['mc_bump_count'] = 160
    mems_gpu[3]['wires_per_mc'] = 160
    mems_gpu[3]['theta_ca'] = 0.28894
    mems_gpu[3]["use_intp"] = 0
    mems_gpu[3]['mem_cost_per_mc'] = 41.99
    mems_gpu[3]['l3_bw'] = 30E9
    mems_gpu[3]['T_j_max'] = 110

    mems_gpu.append({})
    mems_gpu[4]['name'] = "DDR5-4800 4Ch theta_ca=0.24365"
    mems_gpu[4]['mc_bw'] = 2400E6 * 2 * 8
    mems_gpu[4]['mc_count'] = 4
    mems_gpu[4]['mc_area'] = 10E-6
    mems_gpu[4]['mc_freq'] = 2400E6
    mems_gpu[4]['energy_per_wire'] = 15E-12
    mems_gpu[4]['bump_pitch_die'] = 150E-6
    mems_gpu[4]['current_per_bump_die'] = 520.8333333E-3
    mems_gpu[4]['mc_bump_count'] = 160
    mems_gpu[4]['wires_per_mc'] = 160
    mems_gpu[4]['theta_ca'] = 0.24365     
    mems_gpu[4]["use_intp"] = 0
    mems_gpu[4]['mem_cost_per_mc'] = 52.99
    mems_gpu[4]['l3_bw'] = 30E9
    mems_gpu[4]['T_j_max'] = 110

    mems_gpu.append({})
    mems_gpu[5]['name'] = "DDR5-4800 6Ch theta_ca=0.20114"
    mems_gpu[5]['mc_bw'] = 2400E6 * 2 * 8
    mems_gpu[5]['mc_count'] = 6
    mems_gpu[5]['mc_area'] = 10E-6
    mems_gpu[5]['mc_freq'] = 2400E6
    mems_gpu[5]['energy_per_wire'] = 15E-12
    mems_gpu[5]['bump_pitch_die'] = 150E-6
    mems_gpu[5]['current_per_bump_die'] = 520.8333333E-3
    mems_gpu[5]['mc_bump_count'] = 160
    mems_gpu[5]['wires_per_mc'] = 160
    mems_gpu[5]['theta_ca'] = 0.20114
    mems_gpu[5]["use_intp"] = 0
    mems_gpu[5]['mem_cost_per_mc'] = 52.99
    mems_gpu[5]['l3_bw'] = 30E9
    mems_gpu[5]['T_j_max'] = 110

    mems_gpu.append({})
    mems_gpu[6]['name'] = "DDR5-5600 4Ch theta_ca=0.20906"
    mems_gpu[6]['mc_bw'] = 2800E6 * 2 * 8
    mems_gpu[6]['mc_count'] = 4
    mems_gpu[6]['mc_area'] = 10E-6
    mems_gpu[6]['mc_freq'] = 2800E6
    mems_gpu[6]['energy_per_wire'] = 15E-12
    mems_gpu[6]['bump_pitch_die'] = 150E-6
    mems_gpu[6]['current_per_bump_die'] = 520.8333333E-3
    mems_gpu[6]['mc_bump_count'] = 160
    mems_gpu[6]['wires_per_mc'] = 160
    mems_gpu[6]['theta_ca'] = 0.20906     # MIDLINE 0.20906
    mems_gpu[6]["use_intp"] = 0
    mems_gpu[6]['mem_cost_per_mc'] = 73.99
    mems_gpu[6]['l3_bw'] = 30E9
    mems_gpu[6]['T_j_max'] = 110

    mems_gpu.append({})
    mems_gpu[7]['name'] = "DDR5-5600 4Ch theta_ca=0.20268"
    mems_gpu[7]['mc_bw'] = 2800E6 * 2 * 8
    mems_gpu[7]['mc_count'] = 4
    mems_gpu[7]['mc_area'] = 10E-6
    mems_gpu[7]['mc_freq'] = 2800E6
    mems_gpu[7]['energy_per_wire'] = 15E-12
    mems_gpu[7]['bump_pitch_die'] = 150E-6
    mems_gpu[7]['current_per_bump_die'] = 520.8333333E-3
    mems_gpu[7]['mc_bump_count'] = 160
    mems_gpu[7]['wires_per_mc'] = 160
    mems_gpu[7]['theta_ca'] = 0.20268     
    mems_gpu[7]["use_intp"] = 0
    mems_gpu[7]['mem_cost_per_mc'] = 73.99
    mems_gpu[7]['l3_bw'] = 30E9
    mems_gpu[7]['T_j_max'] = 110

    mems_gpu.append({})
    mems_gpu[8]['name'] = "DDR5-5600 6Ch theta_ca=0.15565"
    mems_gpu[8]['mc_bw'] = 2800E6 * 2 * 8
    mems_gpu[8]['mc_count'] = 6
    mems_gpu[8]['mc_area'] = 10E-6
    mems_gpu[8]['mc_freq'] = 2800E6
    mems_gpu[8]['energy_per_wire'] = 15E-12
    mems_gpu[8]['bump_pitch_die'] = 150E-6
    mems_gpu[8]['current_per_bump_die'] = 520.8333333E-3
    mems_gpu[8]['mc_bump_count'] = 160
    mems_gpu[8]['wires_per_mc'] = 160
    mems_gpu[8]['theta_ca'] = 0.15565
    mems_gpu[8]["use_intp"] = 0
    mems_gpu[8]['mem_cost_per_mc'] = 73.99
    mems_gpu[8]['l3_bw'] = 30E9
    mems_gpu[8]['T_j_max'] = 110

    mems_gpu.append({})
    mems_gpu[9]['name'] = "HBM2 3Ch theta_ca=0.3062"
    mems_gpu[9]['mc_bw'] = 850E6 * 2 * 1024            # mem freq * double data rate * bus width
    mems_gpu[9]['mc_count'] = 3                        # 3 Channel since TITAN V bus is 3072b wide      
    mems_gpu[9]['mc_area'] = 6.6831E-6
    mems_gpu[9]['mc_freq'] = 850E6                     # Spec gives 1700 MT/s but it is double data rate	
    mems_gpu[9]['energy_per_wire'] = 3.5E-12
    mems_gpu[9]['bump_pitch_die'] = 50E-6
    mems_gpu[9]['current_per_bump_die'] = 57.87037E-3
    mems_gpu[9]['mc_bump_count'] = 1024
    mems_gpu[9]['wires_per_mc'] = 1024
    mems_gpu[9]['theta_ca'] = 0.3062
    mems_gpu[9]["use_intp"] = 1
    mems_gpu[9]['mem_cost_per_mc'] = 120
    mems_gpu[9]['l3_bw'] = 30E9
    mems_gpu[9]['T_j_max'] = 110

    with open("mems_gpu.json", "w") as outfile:
        json.dump(mems_gpu, outfile)

    l3_configs_gpu = []
    for i in range(1, 51):
        l3_configs_gpu.append({"name": f"{i}x L3s", "l3_count":i})
    
    with open("l3_configs_gpu.json", "w") as outfile:
        json.dump(l3_configs_gpu, outfile)


    ai_apps_gpu = [0.25, 0.5, 1]
    workset_sizes_gpu = [100E6, 50E6 , 25E6]
    # workset_sizes_gpu = [100E6 * ((96E3 / 64) + (4.5E6 / 5120))/(64E3+1E6), 50E6 * ((96E3 / 64) + (4.5E6 / 5120))/(64E3+1E6), 25E6 * ((96E3 / 64) + (4.5E6 / 5120))/(64E3+1E6)]           # smaller workset size for each SP, computed from L1+L2 ratio between CPU and GPU
    app_props_gpu = []
    for ai_app in ai_apps_gpu:
        for workset_size in workset_sizes_gpu:
            app_props_gpu.append({"name": f'{ai_app} App. AI, {workset_size/1E6} MB Workset',
                              "ai_app": ai_app,
                              "workset_size": workset_size})
    
    with open("app_props_gpu.json", "w") as outfile:
        json.dump(app_props_gpu, outfile)

def solve(obj, useGPU, perfLB, areaUB, powerUB, costUB, calibrate_theta_ca):

    results = []
    calibrated_theta_ca = {}

    print(f'Solving for objective {obj} with perfLB={perfLB} Gflop/s, areaUB={areaUB} mm2, powerUB={powerUB} W, costUB=${costUB}\n')
    
    with open("default.json", 'r') as fp:
        master_default = json.load(fp)

    if(useGPU == False):
        concatFileName = ""
    else:
        concatFileName = "_gpu"

    with open("cores" + concatFileName + ".json", 'r') as fp:
        cores = json.load(fp)

    with open("mems" + concatFileName + ".json", 'r') as fp:
        mems = json.load(fp)

    with open("l3_configs" + concatFileName + ".json", 'r') as fp:
        l3_configs = json.load(fp)

    with open("app_props" + concatFileName + ".json", 'r') as fp:
        app_props = json.load(fp)


    for app_prop in app_props:
        for l3_config in l3_configs:
            for mem in mems:
                for core in cores:

                    # Get a new, clean copy of default
                    default = {}
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
                    p.costUB = costUB

                    # ****************************** MODEL EQUATIONS ******************************

                    # Compute max power allowed by thermal constraint.
                    p.theta_ja = (p.theta_jc + p.theta_ca)*(p.theta_jb + p.theta_ba)/(p.theta_jc + p.theta_ca + p.theta_jb + p.theta_ba)
                    p.delta_T = p.T_j_max - p.T_ambient
                    p.P_max_pkg = p.delta_T / p.theta_ja

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

                    p.power_bump_count_die = (p.P_die) / (p.die_voltage * p.current_per_bump_die) * 2

                    # number of cores = number of L1 = number of L2
                    p.A_die_components  = p.core_count * p.core_area * p.core_area_multiplier
                    p.A_die_components += p.core_count * p.l1_area * p.l1l2_area_multiplier
                    p.A_die_components += p.core_count * p.l2_area * p.l1l2_area_multiplier
                    p.A_die_components += p.l3_count   * p.l3_area 
                    p.A_die_components += p.mc_count   * p.mc_area
                    p.A_die_components += p.io_count   * p.io_area 

                    if(p.use_intp == 0):
                        ## DDR System
                        p.A_die_bump = (p.bump_pitch_die**2) * (p.power_bump_count_die + p.mc_bump_count * p.mc_count + p.io_bump_count * p.io_count)
                    else:
                        ## HBM System
                        p.A_die_bump = (p.bump_pitch_intp**2) * (p.power_bump_count_die + p.io_bump_count * p.io_count) + (p.bump_pitch_die**2) * (p.mc_bump_count * p.mc_count)

                    if(p.A_die_bump > p.A_die_components):
                        p.dead_space_die = p.A_die_bump - p.A_die_components
                    else:
                        p.dead_space_die = 0.0

                    p.A_die = max(p.A_die_components, p.A_die_bump)

                    p.max_wire_die = 6 * math.sqrt(p.A_die / 6) * p.package_layer / p.link_pitch

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

                    # Cost Model

                    # area of die for yield calculation purposes
                    # cache peripheral circuitry percentage estimated by CACTI
                    p.A_die_yield  = p.core_count * p.core_area * p.core_area_multiplier
                    p.A_die_yield += p.core_count * p.l1_area * p.l1l2_area_multiplier * 0.79798722
                    p.A_die_yield += p.core_count * p.l2_area * p.l1l2_area_multiplier * 0.4791373467
                    p.A_die_yield += p.l3_count   * p.l3_area * 0.3816312618
                    p.A_die_yield += p.mc_count   * p.mc_area
                    p.A_die_yield += p.io_count   * p.io_area

                    # yield of the die
                    p.die_yield = math.pow((1 + (p.A_die_yield * p.defect_density_die / p.clustering_factor_die)), -1.0 * p.clustering_factor_die)
                    
                    # number of dies that can be cut from a wafer (not considering scribe line and edge exclusion)
                    # note that normal die area, not yield die area, is used for this calculation
                    p.die_per_wafer = p.wafer_dia_die * math.pi * ((p.wafer_dia_die / (4 * p.A_die)) - (1 / math.sqrt(2 * p.A_die)))
                    
                    # cost of each die, considering yield
                    p.die_cost = p.wafer_cost_die / (p.die_per_wafer * p.die_yield)

                    # cost of memory
                    p.mem_cost = p.mc_count * p.mem_cost_per_mc

                    # cost of interposer
                    if(p.use_intp == 0):
                        ## DDR System
                        p.A_intp = 0 
                        p.A_intp_yield = 0
                        p.intp_yield = 0
                        p.intp_per_wafer = 0
                        p.intp_cost = 0
                    else:
                        ## HBM System

                        # area of interposer
                        p.A_intp = p.A_die + (p.mc_count * p.HBM_area_per_mc)

                        # area of interposer for yield calculation purposes
                        p.A_intp_yield = p.A_die_yield + (p.mc_count * p.HBM_area_per_mc)

                        # yield of interposer
                        p.intp_yield = math.pow((1 + (p.A_intp_yield * p.defect_density_intp / p.clustering_factor_intp)), -1.0 * p.clustering_factor_intp)

                        # number of interposers that can be cut from a wafer (not considering scribe line and edge exclusion)
                        p.intp_per_wafer = p.wafer_dia_intp * math.pi * ((p.wafer_dia_intp / (4 * p.A_intp)) - (1 / math.sqrt(2 * p.A_intp)))

                        p.intp_cost = (p.wafer_cost_intp / (p.intp_per_wafer * p.intp_yield)) + p.intp_asm_cost

                    # power consumed by memory that is part of the package
                    if(p.use_intp == 0):
                        ## DDR System
                        p.in_pkg_mem_power = 0.0
                    else:
                        ## HBM System
                        p.in_pkg_mem_power = p.HBM_power_per_mc * p.mc_count
                    
                    # power of the entire package
                    p.P_pkg = p.P_die + p.in_pkg_mem_power

                    # number of power bumps on the package
                    p.power_bump_count_pkg = (p.P_pkg) / (p.die_voltage * p.current_per_bump_pkg) * 2

                    # area of package
                    if(p.use_intp == 0):
                        ## DDR System
                        p.A_pkg = (pow(p.bump_pitch_pkg, 2) * (p.power_bump_count_pkg + p.mc_bump_count * p.mc_count + p.io_bump_count * p.io_count)) + p.pkg_non_io_area
                    else:
                        ## HBM System
                        p.A_pkg = (pow(p.bump_pitch_pkg, 2) * (p.power_bump_count_pkg + p.io_bump_count * p.io_count)) + p.pkg_non_io_area
                    
                    # cost of package
                    p.pkg_cost = p.A_pkg * p.pkg_cost_per_sqmm

                    # total cost 
                    p.cost = p.die_cost + p.intp_cost + p.mem_cost + p.pkg_cost 

                    # ****************************** ENFORCE OBJ-INDEPENDENT CONSTRAINTS ******************************
                    if(p.core_count < 1 or p.l3_count < 1 or p.mc_count < 1 or p.io_count < 1):
                        infs_handler(result, "must have at least one of each component")
                    
                    if(p.core_freq < p.core_freq_min or p.core_freq > p.core_freq_absolute_max):
                        infs_handler(result, "core_freq out of range")
                    
                    if(p.P_max_pkg < p.P_pkg):
                        infs_handler(result, "P_max_pkg < P_pkg")
                    
                    if(p.max_wire_die < p.mc_count * p.wires_per_mc):
                        infs_handler(result, "wire constraint not met")

                    if(p.use_intp == 0):
                        ## DDR System
                        if(p.A_pkg < p.A_die):
                            infs_handler(result, "A_pkg < A_die")
                    else:
                        ## HBM System
                        if(p.A_intp < p.A_die):
                            infs_handler(result, "A_intp < A_die")

                        if(p.A_pkg < p.A_intp):
                            infs_handler(result, "A_pkg < A_intp")

                        if(p.A_pkg < p.A_die):
                            infs_handler(result, "A_pkg < A_die")

                    if(p.dead_space_die > 0):
                        infs_handler(result, "dead_space_die > 0")
                    
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
                        if(p.costUB < p.cost):
                            infs_handler(result, f'costUB < cost')
                        result["obj value"] = p.perf

                    elif(obj == "min_area"):
                        if(p.perf < p.perfLB):
                            infs_handler(result, f'perf < perfLB')
                        if(p.powerUB < p.P_die):
                            infs_handler(result, f'powerUB < P_die')
                        if(p.costUB < p.cost):
                            infs_handler(result, f'costUB < cost')
                        result["obj value"] = p.A_die

                    elif(obj == "min_power"):
                        if(p.areaUB < p.A_die):
                            infs_handler(result, f'areaUB < A_die')
                        if(p.perf < p.perfLB):
                            infs_handler(result, f'perf < perfLB')
                        if(p.costUB < p.cost):
                            infs_handler(result, f'costUB < cost')
                        result["obj value"] = p.P_die

                    # ******************************************************************************************
                    
                    result["perf"] = p.perf
                    result["A_die"] = p.A_die
                    result["P_die"] = p.P_die
                    result["core_freq"] = p.core_freq
                    result["cost"] = p.cost
                    result["dead_space_die"] = p.dead_space_die

                    # Dump the entire namespace with all model param/variables
                    result["dump"] = copy.deepcopy(p.__dict__)

                    # calculate theta_ca @ max P_pkg which takes place at 50 L3 slices
                    if(calibrate_theta_ca == True and p.l3_count == 50):
                        reverse_theta_ja = (p.T_j_max - p.T_ambient) / p.P_pkg

                        reverse_theta_ca = (p.theta_jc * p.theta_jb + p.theta_jc * p.theta_ba - reverse_theta_ja * p.theta_jc - reverse_theta_ja * p.theta_jb - p.theta_ba * reverse_theta_ja)
                        reverse_theta_ca /= (reverse_theta_ja - p.theta_jb - p.theta_ba)

                        calibrated_theta_ca[mem['name']] = reverse_theta_ca

                    results.append(result)

    return results, calibrated_theta_ca

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
        elif(key == 'dead_space_die'):
            if(value < 0.001 or value > 1000):
                print(f'{bcolors.OKCYAN}{key} = {sn_format(value)}{bcolors.ENDC}')
            else:
                print(f'{bcolors.OKCYAN}{key} = {value}{bcolors.ENDC}')
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

def multi_line_plot(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y1_label, y2_label, y3_label, y4_label, y5_label, y6_label, y7_label, y8_label, y9_label, y10_label, x_axis_label, y_axis_label, title):
    plt.figure(figsize=(12, 8))
    plt.plot(x1, y1, **{'color': 'blue', 'marker': 'o'}, label=y1_label, linestyle='-')
    plt.plot(x2, y2, **{'color': 'blue', 'marker': 'D'}, label=y2_label, linestyle='-')
    plt.plot(x3, y3, **{'color': 'purple', 'marker': 'o'}, label=y3_label, linestyle='-')
    plt.plot(x4, y4, **{'color': 'purple', 'marker': 'D'}, label=y4_label, linestyle='-')
    plt.plot(x5, y5, **{'color': 'gold', 'marker': 'o'}, label=y5_label, linestyle='-')
    plt.plot(x6, y6, **{'color': 'gold', 'marker': 'D'}, label=y6_label, linestyle='-')
    plt.plot(x7, y7, **{'color': 'grey', 'marker': 'o'}, label=y7_label, linestyle='-', linewidth=10)
    plt.plot(x8, y8, **{'color': 'darkorange', 'marker': 'o'}, label=y8_label, linestyle='-')
    plt.plot(x9, y9, **{'color': 'darkorange', 'marker': 'D'}, label=y9_label, linestyle='-')
    plt.plot(x10, y10, **{'color': 'red', 'marker': 'o'}, label=y10_label, linestyle='-')

    plt.title(title, fontweight ='bold', fontsize = 15)
    plt.xlabel(x_axis_label, fontweight ='bold', fontsize = 15)
    plt.ylabel(y_axis_label, fontweight ='bold', fontsize = 15)
    plt.legend()

    plt.savefig(f'results/{title}.pdf')
    plt.close()

def multi_scatter_plot(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, y1, y2, y3, y4, y5, y6, y7, y8, y9, y10, y1_label, y2_label, y3_label, y4_label, y5_label, y6_label, y7_label, y8_label, y9_label, y10_label, x_axis_label, y_axis_label, title):

    plt.figure(figsize=(12, 8))
    plt.scatter(x1, y1, c ="blue", linewidths = 0, marker ="o", edgecolor ="black", s = 50, label=y1_label)
    plt.scatter(x2, y2, c ="blue", linewidths = 0, marker ="D", edgecolor ="black", s = 100, label=y2_label)
    plt.scatter(x3, y3, c ="purple", linewidths = 0, marker ="o", edgecolor ="black", s = 50, label=y3_label)
    plt.scatter(x4, y4, c ="purple", linewidths = 0, marker ="D", edgecolor ="black", s = 100, label=y4_label)
    plt.scatter(x5, y5, c ="gold", linewidths = 0, marker ="o", edgecolor ="black", s = 50, label=y5_label)
    plt.scatter(x6, y6, c ="gold", linewidths = 0, marker ="D", edgecolor ="black", s = 100, label=y6_label)
    plt.scatter(x7, y7, c ="grey", linewidths = 0, marker ="o", edgecolor ="black", s = 50, label=y7_label)
    plt.scatter(x8, y8, c ="darkorange", linewidths = 0, marker ="o", edgecolor ="black", s = 50, label=y8_label)
    plt.scatter(x9, y9, c ="darkorange", linewidths = 0, marker ="D", edgecolor ="black", s = 100, label=y9_label)
    plt.scatter(x10, y10, c ="red", linewidths = 0, marker ="o", edgecolor ="black", s = 50, label=y10_label)

    plt.title(title, fontweight ='bold', fontsize = 15)
    plt.xlabel(x_axis_label, fontweight ='bold', fontsize = 15)
    plt.ylabel(y_axis_label, fontweight ='bold', fontsize = 15)
    plt.legend()
    plt.savefig(f'results/{title}.pdf')
    plt.close()

def plot(results, useGPU):

    if(useGPU == False):
        concatFileName = ""
        concatTitleName = ""
    else:
        concatFileName = "_gpu"
        concatTitleName = "[G]"

    with open("app_props" + concatFileName + ".json", 'r') as fp:
        app_props = json.load(fp)

    with open("mems" + concatFileName + ".json", 'r') as fp:
        mems = json.load(fp)

    for app_prop in app_props:
        # "results" is a list of dicts where each dict corresponds to a specific design point and its associated data
        # MEM_TYPE_COUNT is the number of different memories considered as part of the DSE

        # a list of MEM_TYPE_COUNT lists, each of which has the same hierarchy as "results", just shorter
        mem_raw_data = []

        # a list of MEM_TYPE_COUNT dicts, each of which has (key, value) pairs = (plot axis, list of values for that axis)
        mem_plot_data = [] 

        # format mem_plot_data before filling it with data
        for i in range(len(mems)):
            mem_plot_data.append({"l3_count": [], "perf": [], "l3_bound": [], "mc_bound": [], "compute_bound": [], "io_bound": [], "die_cost": [], "mem_cost": [], "intp_cost": [], "pkg_cost": [], "cost": []})

        # filter all results into a subset which has a specific app profile
        # nothing changes, simply removing all entries from "results" that does not have the current "app_prop" 
        curr = [result for result in results if result["app_prop"]["ai_app"] == app_prop["ai_app"]]
        curr = [result for result in curr if result["app_prop"]["workset_size"] == app_prop["workset_size"]]

        # divide "curr" into a seperate list for each memory type
        for i in range(len(mems)):
            mem_raw_data.append([result for result in curr if result["mem"]["name"] == mems[i]["name"]])

        # grab ai_app, workset_size, and arithmetic_intensity for plot titles
        ai_app = app_prop["ai_app"]
        workset_size = app_prop["workset_size"] / 1E6
        arithmetic_intensity = curr[0]['dump']['arithmetic_intensity'] # only works because l1/l2_capacity are constants in the whole experiment

        # convert mem_raw_data to mem_plot_data
        for i in range(len(mems)): 
            for result in mem_raw_data[i]:
                mem_plot_data[i]["l3_count"].append(result['dump']['l3_count'])
                mem_plot_data[i]["perf"].append(result['dump']['perf'])
                mem_plot_data[i]["l3_bound"].append(result['dump']['l3_bound'])
                mem_plot_data[i]["mc_bound"].append(result['dump']['mc_bound'])
                mem_plot_data[i]["compute_bound"].append(result['dump']['compute_bound'])
                mem_plot_data[i]["io_bound"].append(result['dump']['io_bound'])
                mem_plot_data[i]["die_cost"].append(result['dump']['die_cost'])
                mem_plot_data[i]["mem_cost"].append(result['dump']['mem_cost'])
                mem_plot_data[i]["intp_cost"].append(result['dump']['intp_cost'])
                mem_plot_data[i]["pkg_cost"].append(result['dump']['pkg_cost'])
                mem_plot_data[i]["cost"].append(result['dump']['cost'])

        
        # rescale mem_plot_data (adding the "Giga" prefix) 
        for i in range(len(mems)):
            mem_plot_data[i]["perf"] = np.array(mem_plot_data[i]["perf"]) / 1E9
            mem_plot_data[i]["l3_bound"] = np.array(mem_plot_data[i]["l3_bound"]) / 1E9
            mem_plot_data[i]["mc_bound"] = np.array(mem_plot_data[i]["mc_bound"]) / 1E9
            mem_plot_data[i]["compute_bound"] = np.array(mem_plot_data[i]["compute_bound"]) / 1E9
            mem_plot_data[i]["io_bound"] = np.array(mem_plot_data[i]["io_bound"]) / 1E9

        # plot
        multi_scatter_plot(x1=mem_plot_data[0]["perf"], x2=mem_plot_data[1]["perf"], x3=mem_plot_data[2]["perf"], x4=mem_plot_data[3]["perf"], x5=mem_plot_data[4]["perf"], x6=mem_plot_data[5]["perf"], x7=mem_plot_data[6]["perf"], x8=mem_plot_data[7]["perf"], x9=mem_plot_data[8]["perf"], x10=mem_plot_data[9]["perf"], 
                           y1=mem_plot_data[0]["cost"], y2=mem_plot_data[1]["cost"], y3=mem_plot_data[2]["cost"], y4=mem_plot_data[3]["cost"], y5=mem_plot_data[4]["cost"], y6=mem_plot_data[5]["cost"], y7=mem_plot_data[6]["cost"], y8=mem_plot_data[7]["cost"], y9=mem_plot_data[8]["cost"], y10=mem_plot_data[9]["cost"], 
                           y1_label=mems[0]['name'], y2_label=mems[1]['name'], y3_label=mems[2]['name'], y4_label=mems[3]['name'], y5_label=mems[4]['name'], y6_label=mems[5]['name'], y7_label=mems[6]['name'], y8_label=mems[7]['name'], y9_label=mems[8]['name'], y10_label=mems[9]['name'], 
                           x_axis_label='Performance (Gflop/s)', y_axis_label='Cost (USD)',
                           title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] DDR vs HBM Design Space Exploration')

        multi_line_plot(x1=mem_plot_data[0]["l3_count"], x2=mem_plot_data[1]["l3_count"], x3=mem_plot_data[2]["l3_count"], x4=mem_plot_data[3]["l3_count"], x5=mem_plot_data[4]["l3_count"], x6=mem_plot_data[5]["l3_count"], x7=mem_plot_data[6]["l3_count"], x8=mem_plot_data[7]["l3_count"], x9=mem_plot_data[8]["l3_count"], x10=mem_plot_data[9]["l3_count"], 
                        y1=mem_plot_data[0]["perf"], y2=mem_plot_data[1]["perf"], y3=mem_plot_data[2]["perf"], y4=mem_plot_data[3]["perf"], y5=mem_plot_data[4]["perf"], y6=mem_plot_data[5]["perf"], y7=mem_plot_data[6]["perf"], y8=mem_plot_data[7]["perf"], y9=mem_plot_data[8]["perf"], y10=mem_plot_data[9]["perf"], 
                        y1_label=mems[0]['name'], y2_label=mems[1]['name'], y3_label=mems[2]['name'], y4_label=mems[3]['name'], y5_label=mems[4]['name'], y6_label=mems[5]['name'], y7_label=mems[6]['name'], y8_label=mems[7]['name'], y9_label=mems[8]['name'], y10_label=mems[9]['name'], 
                        x_axis_label='Number of L3 Slices', y_axis_label='Performance (Gflop/s)',
                        title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] DDR vs HBM Performance')

        multi_line_plot(x1=mem_plot_data[0]["l3_count"], x2=mem_plot_data[1]["l3_count"], x3=mem_plot_data[2]["l3_count"], x4=mem_plot_data[3]["l3_count"], x5=mem_plot_data[4]["l3_count"], x6=mem_plot_data[5]["l3_count"], x7=mem_plot_data[6]["l3_count"], x8=mem_plot_data[7]["l3_count"], x9=mem_plot_data[8]["l3_count"], x10=mem_plot_data[9]["l3_count"], 
                        y1=mem_plot_data[0]["die_cost"], y2=mem_plot_data[1]["die_cost"], y3=mem_plot_data[2]["die_cost"], y4=mem_plot_data[3]["die_cost"], y5=mem_plot_data[4]["die_cost"], y6=mem_plot_data[5]["die_cost"], y7=mem_plot_data[6]["die_cost"], y8=mem_plot_data[7]["die_cost"], y9=mem_plot_data[8]["die_cost"], y10=mem_plot_data[9]["die_cost"], 
                        y1_label=mems[0]['name'], y2_label=mems[1]['name'], y3_label=mems[2]['name'], y4_label=mems[3]['name'], y5_label=mems[4]['name'], y6_label=mems[5]['name'], y7_label=mems[6]['name'], y8_label=mems[7]['name'], y9_label=mems[8]['name'], y10_label=mems[9]['name'], 
                        x_axis_label='Number of L3 Slices', y_axis_label='Cost (USD)',
                        title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] DDR vs HBM Die Cost')

        multi_line_plot(x1=mem_plot_data[0]["l3_count"], x2=mem_plot_data[1]["l3_count"], x3=mem_plot_data[2]["l3_count"], x4=mem_plot_data[3]["l3_count"], x5=mem_plot_data[4]["l3_count"], x6=mem_plot_data[5]["l3_count"], x7=mem_plot_data[6]["l3_count"], x8=mem_plot_data[7]["l3_count"], x9=mem_plot_data[8]["l3_count"], x10=mem_plot_data[9]["l3_count"], 
                        y1=mem_plot_data[0]["mem_cost"], y2=mem_plot_data[1]["mem_cost"], y3=mem_plot_data[2]["mem_cost"], y4=mem_plot_data[3]["mem_cost"], y5=mem_plot_data[4]["mem_cost"], y6=mem_plot_data[5]["mem_cost"], y7=mem_plot_data[6]["mem_cost"], y8=mem_plot_data[7]["mem_cost"], y9=mem_plot_data[8]["mem_cost"], y10=mem_plot_data[9]["mem_cost"], 
                        y1_label=mems[0]['name'], y2_label=mems[1]['name'], y3_label=mems[2]['name'], y4_label=mems[3]['name'], y5_label=mems[4]['name'], y6_label=mems[5]['name'], y7_label=mems[6]['name'], y8_label=mems[7]['name'], y9_label=mems[8]['name'], y10_label=mems[9]['name'], 
                        x_axis_label='Number of L3 Slices', y_axis_label='Cost (USD)',
                        title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] DDR vs HBM Memory Cost')

        multi_line_plot(x1=mem_plot_data[0]["l3_count"], x2=mem_plot_data[1]["l3_count"], x3=mem_plot_data[2]["l3_count"], x4=mem_plot_data[3]["l3_count"], x5=mem_plot_data[4]["l3_count"], x6=mem_plot_data[5]["l3_count"], x7=mem_plot_data[6]["l3_count"], x8=mem_plot_data[7]["l3_count"], x9=mem_plot_data[8]["l3_count"], x10=mem_plot_data[9]["l3_count"], 
                        y1=mem_plot_data[0]["intp_cost"], y2=mem_plot_data[1]["intp_cost"], y3=mem_plot_data[2]["intp_cost"], y4=mem_plot_data[3]["intp_cost"], y5=mem_plot_data[4]["intp_cost"], y6=mem_plot_data[5]["intp_cost"], y7=mem_plot_data[6]["intp_cost"], y8=mem_plot_data[7]["intp_cost"], y9=mem_plot_data[8]["intp_cost"], y10=mem_plot_data[9]["intp_cost"], 
                        y1_label=mems[0]['name'], y2_label=mems[1]['name'], y3_label=mems[2]['name'], y4_label=mems[3]['name'], y5_label=mems[4]['name'], y6_label=mems[5]['name'], y7_label=mems[6]['name'], y8_label=mems[7]['name'], y9_label=mems[8]['name'], y10_label=mems[9]['name'], 
                        x_axis_label='Number of L3 Slices', y_axis_label='Cost (USD)',
                        title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] DDR vs HBM Interposer Cost')

        multi_line_plot(x1=mem_plot_data[0]["l3_count"], x2=mem_plot_data[1]["l3_count"], x3=mem_plot_data[2]["l3_count"], x4=mem_plot_data[3]["l3_count"], x5=mem_plot_data[4]["l3_count"], x6=mem_plot_data[5]["l3_count"], x7=mem_plot_data[6]["l3_count"], x8=mem_plot_data[7]["l3_count"], x9=mem_plot_data[8]["l3_count"], x10=mem_plot_data[9]["l3_count"], 
                        y1=mem_plot_data[0]["pkg_cost"], y2=mem_plot_data[1]["pkg_cost"], y3=mem_plot_data[2]["pkg_cost"], y4=mem_plot_data[3]["pkg_cost"], y5=mem_plot_data[4]["pkg_cost"], y6=mem_plot_data[5]["pkg_cost"], y7=mem_plot_data[6]["pkg_cost"], y8=mem_plot_data[7]["pkg_cost"], y9=mem_plot_data[8]["pkg_cost"], y10=mem_plot_data[9]["pkg_cost"], 
                        y1_label=mems[0]['name'], y2_label=mems[1]['name'], y3_label=mems[2]['name'], y4_label=mems[3]['name'], y5_label=mems[4]['name'], y6_label=mems[5]['name'], y7_label=mems[6]['name'], y8_label=mems[7]['name'], y9_label=mems[8]['name'], y10_label=mems[9]['name'], 
                        x_axis_label='Number of L3 Slices', y_axis_label='Cost (USD)',
                        title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] DDR vs HBM Package Cost')

        multi_line_plot(x1=mem_plot_data[0]["l3_count"], x2=mem_plot_data[1]["l3_count"], x3=mem_plot_data[2]["l3_count"], x4=mem_plot_data[3]["l3_count"], x5=mem_plot_data[4]["l3_count"], x6=mem_plot_data[5]["l3_count"], x7=mem_plot_data[6]["l3_count"], x8=mem_plot_data[7]["l3_count"], x9=mem_plot_data[8]["l3_count"], x10=mem_plot_data[9]["l3_count"], 
                        y1=mem_plot_data[0]["cost"], y2=mem_plot_data[1]["cost"], y3=mem_plot_data[2]["cost"], y4=mem_plot_data[3]["cost"], y5=mem_plot_data[4]["cost"], y6=mem_plot_data[5]["cost"], y7=mem_plot_data[6]["cost"], y8=mem_plot_data[7]["cost"], y9=mem_plot_data[8]["cost"], y10=mem_plot_data[9]["cost"], 
                        y1_label=mems[0]['name'], y2_label=mems[1]['name'], y3_label=mems[2]['name'], y4_label=mems[3]['name'], y5_label=mems[4]['name'], y6_label=mems[5]['name'], y7_label=mems[6]['name'], y8_label=mems[7]['name'], y9_label=mems[8]['name'], y10_label=mems[9]['name'], 
                        x_axis_label='Number of L3 Slices', y_axis_label='Cost (USD)',
                        title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] DDR vs HBM Cost')

        double_line_plot(x1=mem_plot_data[0]["l3_count"], x2=mem_plot_data[0]["l3_count"], 
                         y1=mem_plot_data[0]["compute_bound"], y2=mem_plot_data[0]["io_bound"], 
                         y1_label='Compute Throughput', y2_label='Memory Bandwidth',
                         x_axis_label='Number of L3 Slices', y_axis_label='',
                         title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] DDR4-2400 4Ch Compute vs IO Bound')

        double_line_plot(x1=mem_plot_data[0]["l3_count"], x2=mem_plot_data[0]["l3_count"], 
                         y1=mem_plot_data[0]["l3_bound"], y2=mem_plot_data[0]["mc_bound"], 
                         y1_label='L3 Effective BW', y2_label='MC Effective BW',
                         x_axis_label='Number of L3 Slices', y_axis_label='',
                         title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] DDR4-2400 4Ch L3 vs MC Bound')

        double_line_plot(x1=mem_plot_data[4]["l3_count"], x2=mem_plot_data[4]["l3_count"], 
                         y1=mem_plot_data[4]["compute_bound"], y2=mem_plot_data[4]["io_bound"], 
                         y1_label='Compute Throughput', y2_label='Memory Bandwidth',
                         x_axis_label='Number of L3 Slices', y_axis_label='',
                         title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] DDR5-4800 4Ch Compute vs IO Bound')

        double_line_plot(x1=mem_plot_data[4]["l3_count"], x2=mem_plot_data[4]["l3_count"], 
                         y1=mem_plot_data[4]["l3_bound"], y2=mem_plot_data[4]["mc_bound"], 
                         y1_label='L3 Effective BW', y2_label='MC Effective BW',
                         x_axis_label='Number of L3 Slices', y_axis_label='',
                         title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] DDR5-4800 4Ch L3 vs MC Bound')

        double_line_plot(x1=mem_plot_data[9]["l3_count"], x2=mem_plot_data[9]["l3_count"], 
                         y1=mem_plot_data[9]["compute_bound"], y2=mem_plot_data[9]["io_bound"], 
                         y1_label='Compute Throughput', y2_label='Memory Bandwidth',
                         x_axis_label='Number of L3 Slices', y_axis_label='',
                         title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] HBM2 4Ch Compute vs IO Bound')

        double_line_plot(x1=mem_plot_data[9]["l3_count"], x2=mem_plot_data[9]["l3_count"], 
                         y1=mem_plot_data[9]["l3_bound"], y2=mem_plot_data[9]["mc_bound"], 
                         y1_label='L3 Effective BW', y2_label='MC Effective BW',
                         x_axis_label='Number of L3 Slices', y_axis_label='',
                         title=concatTitleName + f'[{ai_app} App. AI, {"{:.2f}".format(arithmetic_intensity)} Eff. AI, {"{:.2f}".format(workset_size)} MB Workset] HBM2 4Ch L3 vs MC Bound')

def sn_format(value):
    return "{:.4e}".format(value)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    # use -o flag to specify max_perf, min_area, or min_power objective
    parser.add_argument("-o", "--objective", dest = "obj")

    # use -perf -area -power -cost flags to override default values for perf, area, power, and cost limit
    parser.add_argument("-perf", dest = "perfLB", type=float, default="10")
    parser.add_argument("-area", dest = "areaUB", type=float, default="1000")
    parser.add_argument("-power", dest = "powerUB", type=float, default="1E10")
    parser.add_argument("-cost", dest = "costUB", type=float, default="1E10")

    # use -display flag to view key information about every single design point
    # o.w. only print best design point
    parser.add_argument("-display", action='store_true')

    # use -dump flag to view complete information about any design points which are displayed
    parser.add_argument("-dump", action='store_true')

    # use -noplot flag to not generate plots
    parser.add_argument("-noplot", action='store_true')

    # use -theta_ca flag to get calibrated theta_ca values based on P_pkg
    parser.add_argument("-theta_ca", action='store_true')

    # use -gpu flag to apply the framework to GPU architecture
    parser.add_argument("-gpu", action='store_true')

    args = parser.parse_args()
    
    load_data()
    results, calibrated_theta_ca = solve(obj=args.obj, useGPU=args.gpu, 
                                         perfLB=args.perfLB, areaUB=args.areaUB, 
                                         powerUB=args.powerUB, costUB=args.costUB, 
                                         calibrate_theta_ca=args.theta_ca)
    filtered, infs_count = infs_filter(results)

    if(args.display == True):
        display(results=results, dump=args.dump)

    find_best(results=filtered, obj=args.obj, dump=args.dump)
    
    if(args.noplot == False):
        plot(results=filtered, useGPU=args.gpu)

    if(args.theta_ca == True):
        print('######################################################')
        print("Calibrated theta_ca values: ")
        for key, value in calibrated_theta_ca.items():
            print(f'{key}: {math.floor(value * 100000.0)/100000.0}')


    print('######################################################')
    print(f'{len(results)} design points evaluated.')
    if(infs_count == 0):
        print(f'{bcolors.OKGREEN}{infs_count} infeasible design points removed.{bcolors.ENDC}')
    else:
        print(f'{bcolors.FAIL}{infs_count} infeasible design points removed.{bcolors.ENDC}')

