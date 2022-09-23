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
param core_capacitance;        # for the core only, per core


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

var A_die;
var P_die;
var core_power;
var power_bump_count;
var max_wire;
var core_freq;
var peak_perf;
var peak_bw;

s.t. def_A_die: A_die == sum {i in Components} component_counts[i] * component_areas[i];

s.t. def_P_die: P_die == component_counts['core'] * core_power + component_counts['io'] * io_power+
                         component_counts['l3'] * l3_power + component_counts['mc'] * mc_power;

s.t. def_power_bump_count: power_bump_count == (P_die) / (die_voltage * current_per_bump) * 2;

s.t. def_max_wire: max_wire == sqrt((sum {i in Components} component_counts[i] * component_areas[i]) / 6) * 6 * package_layer / link_pitch;

s.t. def_core_power: core_power == core_capacitance * die_voltage * die_voltage * core_freq;

s.t. def_peak_perf: peak_perf == core_freq * IPC * component_counts['core'];

s.t. def_peak_bw: peak_bw == 0.3 * component_counts['l3'] + 0.7 * component_counts['mc']; # Placeholder!


# ****************************** OBJECTIVE ******************************

minimize min_area: A_die;


# ****************************** CONSTRAINTS ******************************

s.t. range {i in Components}: component_counts[i] >= 1;
s.t. power_constraint: P_max >= P_die;
s.t. bump_constraint: A_die >= bump_pitch * bump_pitch * (power_bump_count + mc_bump_count + io_bump_count);
s.t. wire_constraint: max_wire >= component_counts['mc'] * wires_per_mc;
s.t. roofline: peak_perf == arithmetic_intensity * peak_bw;
s.t. performance_theshold: peak_perf >= 200;