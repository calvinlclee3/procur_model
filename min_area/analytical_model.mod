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
param die_voltage;                  # for the entire die
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
param power_ctrl;

# performance parameters
param arithmetic_intensity;    # number of operations per byte of memory transfer
param IPC;                     # instructions per cycle
param capacitance_per_core;    # for the core only, per core
param l3_count_weight;
param mc_count_weight;
param core_freq_max;
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

# Compute power of memory controller.
param power_phys := energy_per_wire * mem_freq * wires_per_mc;
param mc_power := power_phys + power_ctrl;


# ****************************** DECISION VARIABLES ******************************

# number of each component (integer)
var component_counts {i in Components} integer;


# ****************************** DEPENDENT VARIABLES ******************************

var A_die >= 0;
var P_die >= 0;
var core_power >= 0;
var power_bump_count >= 0;
var max_wire >= 0;
var core_freq >= 0;
var f1;
var f2;
var f3;
var b1 binary;
var b2 binary;
var b3 binary;
var peak_perf >= 0;         # also known as compute throughput
var peak_bw >= 0;
var core_freq_area_multiplier >= 0;

s.t. def_A_die: A_die == component_counts['core'] * component_areas['core'] * core_freq_area_multiplier + 
                         component_counts['io']   * component_areas['io'] +
                         component_counts['l3']   * component_areas['l3'] +
                         component_counts['mc']   * component_areas['mc'];

s.t. def_P_die: P_die == component_counts['core'] * core_power + component_counts['io'] * io_power+
                         component_counts['l3'] * l3_power + component_counts['mc'] * mc_power;

s.t. def_core_power: core_power == capacitance_per_core * (die_voltage**2) * core_freq;

s.t. def_power_bump_count: power_bump_count == (P_die) / (die_voltage * current_per_bump) * 2;

s.t. def_max_wire: max_wire == sqrt((sum {i in Components} component_counts[i] * component_areas[i]) / 6) * 6 * package_layer / link_pitch;

s.t. def_core_freq: core_freq == 0*f1 + core_freq_nominal*f2 + core_freq_max*f3;

s.t. SOS2_constraint_1: 0 <= f1 <= 1;
s.t. SOS2_constraint_2: 0 <= f2 <= 1;
s.t. SOS2_constraint_3: 0 <= f3 <= 1;
s.t. SOS2_constraint_4: f1 + f2 + f3 == 1;
s.t. SOS2_constraint_5: f1 <= b1;
s.t. SOS2_constraint_6: f2 <= b2;
s.t. SOS2_constraint_7: f3 <= b3;
s.t. SOS2_constraint_8: b1 + b2 + b3 <= 2;
s.t. SOS2_constraint_9: b1 + b3 <= 1;

s.t. def_peak_perf: peak_perf == core_freq * IPC * component_counts['core'];

s.t. def_peak_bw: peak_bw == l3_count_weight * component_counts['l3'] + mc_count_weight * component_counts['mc']; # Placeholder!

s.t. def_core_freq_area_multiplier: core_freq_area_multiplier == 1*f1 + 1*f2 + (2*core_freq_max/core_freq_nominal - 1)*f3;

# Implementation using AMPL native piece-wise linear function syntax.
# s.t. def_core_freq_area_multiplier: core_freq_area_multiplier == << core_freq_nominal; 0, (1 / core_freq_nominal) * 2 >> core_freq + 1; # REPLACE WITH CORE_FREQ

# ****************************** OBJECTIVE ******************************

# [Minimize Area]
#minimize min_area: A_die;

# [Minimize Power]
#minimize min_power: P_die;

# [Maximize Performance]
maximize max_performance: peak_perf;


# ****************************** OBJECTIVE-INDEPENDENT CONSTRAINTS ******************************

s.t. range {i in Components}: component_counts[i] >= 1;
s.t. freq_constraint: core_freq_max >= core_freq;
#s.t. IPC_constraint: IPC <= IPC_max;
s.t. thermal_constraint: P_max >= P_die; # usual direction
s.t. bump_constraint: A_die >= (bump_pitch**2) * (power_bump_count + mc_bump_count + io_bump_count); # unusual direction
s.t. wire_constraint: max_wire >= component_counts['mc'] * wires_per_mc;
s.t. roofline: peak_perf == arithmetic_intensity * peak_bw;


# ****************************** OBJECTIVE-DEPENDENT CONSTRAINTS ******************************

# [Minimize Area]:
#s.t. performance_constraint: peak_perf >= PerfLB;
#s.t. power_constraint: P_die <= PowerUB;

# [Minimize Power]
#s.t. area_constraint: A_die <= AreaUB;
#s.t. performance_constraint: peak_perf >= PerfLB;

# [Maximize Performance]
s.t. area_constraint: A_die <= AreaUB;
#s.t. power_constraint: P_die <= PowerUB;
