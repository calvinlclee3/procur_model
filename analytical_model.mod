set Components;
# ****************************** PARAMETERS ******************************

# thermal parameters
param theta_jc;
param theta_ca;
param theta_jb;
param theta_ba;  
param T_ambient;
param T_j_max;

# area of each component
param component_areas {i in Components}; 

# power of each component
param l3_power;
param io_power;

# bump parameters
param bump_pitch;
param die_voltage_nominal;
param current_per_bump;
param mc_bump_count;
param io_bump_count;

# wire parameters
param package_layer;
param link_pitch;

# memory controller parameters
param wires_per_mc;
param energy_per_wire;
param mem_freq;
param mc_power_ctrl;                    # per MC

# performance parameters
param ai_app;                       # operations / byte
param IPC;                              # instructions / cycle
param capacitance_per_core;             # for the core only, per core
param l1_capacity;                      # per L1 (L1 is part of the core)
param l2_capacity;                      # per L2 (L2 is part of the core)
param l3_capacity;                      # per "slice" of L3
param l3_hit_rate_nominal;
param l3_bw;                            # per L3
param mc_bw;                            # per MC
param workset_size;                     # size of the working set
param core_freq_min;
param core_freq_base_max;
param core_freq_absolute_max;
param core_freq_nominal;

# objective-dependent constraint
param PerfLB;
param PerfUB;
param AreaLB;
param AreaUB;
param PowerLB;
param PowerUB;

# Compute max power allowed by thermal constraint.
param theta_ja := (theta_jc + theta_ca)*(theta_jb + theta_ba)/(theta_jc + theta_ca + theta_jb + theta_ba);
param delta_T := T_j_max - T_ambient;
param P_max := delta_T / theta_ja; 

# Compute power of a memory controller.
param mc_power_phys := energy_per_wire * mem_freq * wires_per_mc;
param mc_power := mc_power_phys + mc_power_ctrl;

# Compute arithmetic intensity.
param arithmetic_intensity := (l1_capacity + l2_capacity) / workset_size * ai_app;

# ****************************** DECISION VARIABLES ******************************

# number of each component (integer)
var component_counts {i in Components} integer;


# ****************************** DEPENDENT VARIABLES ******************************

var A_die >= 0;
var P_die >= 0;
var core_freq >= 0;
var die_voltage >= 0;                   # scales linearly with core_freq
var core_power >= 0;
var power_bump_count >= 0;
var max_wire >= 0;

var core_freq_max >= 0;
var core_area_multiplier >= 0;
# core_freq_max auxiliary variables
var f1;
var f2;
var f3;
var b1 binary;
var b2 binary;
var b3 binary;

var l3_to_workset_ratio >= 0;
var l3_hit_rate >= 0;
# l3_to_workset_ratio auxiliary variables
var r1;
var r2;
var r3;
var bb1 binary;
var bb2 binary;
var bb3 binary;

var compute_throughput >= 0;        
var system_bw >= 0;
var perf >= 0;


s.t. def_A_die: A_die == component_counts['core'] * component_areas['core'] * core_area_multiplier + 
                         component_counts['io']   * component_areas['io']   +
                         component_counts['l3']   * component_areas['l3']   +
                         component_counts['mc']   * component_areas['mc'];

s.t. def_P_die: P_die == component_counts['core'] * core_power + component_counts['io'] * io_power+
                         component_counts['l3']   * l3_power   + component_counts['mc'] * mc_power;

s.t. def_die_voltage: die_voltage == (core_freq / core_freq_nominal) * die_voltage_nominal;

s.t. def_core_power: core_power == core_freq * capacitance_per_core * (die_voltage**2);

s.t. def_power_bump_count: power_bump_count == (P_die) / (die_voltage * current_per_bump) * 2;

s.t. def_max_wire: max_wire == sqrt((component_counts['core'] * component_areas['core'] * core_area_multiplier + 
                                     component_counts['io']   * component_areas['io']   +
                                     component_counts['l3']   * component_areas['l3']   +
                                     component_counts['mc']   * component_areas['mc']) / 6) * 6 * package_layer / link_pitch;

# 5% increase in core_freq_max -> 10% increase in component_areas['core']
s.t. def_core_freq_max: core_freq_max == 0*f1 + core_freq_base_max*f2 + core_freq_absolute_max*f3;
s.t. def_core_area_multiplier: core_area_multiplier == 1*f1 + 1*f2 + (2*core_freq_absolute_max/core_freq_base_max - 1)*f3;
s.t. core_freq_max_SOS2_1: 0 <= f1 <= 1;
s.t. core_freq_max_SOS2_2: 0 <= f2 <= 1;
s.t. core_freq_max_SOS2_3: 0 <= f3 <= 1;
s.t. core_freq_max_SOS2_4: f1 + f2 + f3 == 1;
s.t. core_freq_max_SOS2_5: f1 <= b1;
s.t. core_freq_max_SOS2_6: f2 <= b2;
s.t. core_freq_max_SOS2_7: f3 <= b3;
s.t. core_freq_max_SOS2_8: b1 + b2 + b3 <= 2;
s.t. core_freq_max_SOS2_9: b1 + b3 <= 1;

# relative size of the working set and the L3 cache determines L3 hit rate
s.t. def_l3_to_workset_ratio_1: (l3_capacity * component_counts['l3']) / workset_size == 0*r1 + 1*r2 + 100*r3;
s.t. def_l3_to_workset_ratio_2: l3_to_workset_ratio == 0*r1 + 1*r2 + 100*r3;
s.t. def_l3_hit_rate: l3_hit_rate == 0*r1 + l3_hit_rate_nominal*r2 + l3_hit_rate_nominal*r3;
s.t. l3_to_workset_ratio_SOS2_1: 0 <= r1 <= 1;
s.t. l3_to_workset_ratio_SOS2_2: 0 <= r2 <= 1;
s.t. l3_to_workset_ratio_SOS2_3: 0 <= r3 <= 1;
s.t. l3_to_workset_ratio_SOS2_4: r1 + r2 + r3 == 1;
s.t. l3_to_workset_ratio_SOS2_5: r1 <= bb1;
s.t. l3_to_workset_ratio_SOS2_6: r2 <= bb2;
s.t. l3_to_workset_ratio_SOS2_7: r3 <= bb3;
s.t. l3_to_workset_ratio_SOS2_8: bb1 + bb2 + bb3 <= 2;
s.t. l3_to_workset_ratio_SOS2_9: bb1 + bb3 <= 1;

s.t. def_compute_throughput: compute_throughput == core_freq * IPC * component_counts['core'];

# All LD/ST go through L3. L3 misses go through main memory.
s.t. def_system_bw_1: system_bw <= l3_bw * component_counts['l3'] / 1;
s.t. def_system_bw_2: system_bw <= mc_bw * component_counts['mc'] / (1 - l3_hit_rate);

# perf = min (compute_throughput, arithmetic_intensity * system_bw) (min not supported by solver)
# The condition above guarantees below, but not the other way around.
# For max performance, it is equivalent, but might not be for min area (i.e. when PerfLB is very small).
s.t. def_perf_1: perf <= compute_throughput;
s.t. def_perf_2: perf <= arithmetic_intensity * system_bw;

# Implementation using AMPL built-in piece-wise linear function syntax (not supported by solver).
# s.t. def_core_area_multiplier: core_area_multiplier == << core_freq_nominal; 0, (1 / core_freq_nominal) * 2 >> core_freq + 1;

# ****************************** OBJECTIVE ******************************

# [Minimize Area]
minimize min_area: A_die;

# [Minimize Power]
#minimize min_power: P_die;

# [Maximize Performance]
#maximize max_performance: perf;

# [Custom Metric]
#maximize custom_metric: ((1/P_die)) * ((1/A_die))* perf;


# ****************************** OBJECTIVE-INDEPENDENT CONSTRAINTS ******************************

s.t. range {i in Components}: component_counts[i] >= 1;
s.t. freq_lower_bound: core_freq >= core_freq_min;
s.t. freq_upper_bound: (0*f1 + core_freq_base_max*f2 + core_freq_absolute_max*f3) >= core_freq;
s.t. thermal_constraint: P_max >= P_die;                                                             # usual direction
s.t. bump_constraint: A_die >= (bump_pitch**2) * (power_bump_count + mc_bump_count + io_bump_count); # unusual direction
s.t. wire_constraint: max_wire >= component_counts['mc'] * wires_per_mc;


# ****************************** OBJECTIVE-DEPENDENT CONSTRAINTS ******************************

# [Minimize Area]:
s.t. performance_constraint: perf >= PerfLB;
#s.t. power_constraint: PowerUB >= P_die;

# [Minimize Power]
#s.t. area_constraint: AreaUB >= A_die;
#s.t. performance_constraint: perf >= PerfLB;

# [Maximize Performance]
#s.t. area_constraint: AreaUB >= A_die;
#s.t. power_constraint: PowerUB >= P_die;

# [Custom Metric]
#s.t. area_constraint: AreaUB >= A_die;
#s.t. performance_constraint: perf >= PerfLB;