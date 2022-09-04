set Components;

param theta_jc;
param theta_ca;
param theta_jb;
param theta_ba;  
param T_ambient;
param T_j_max;

# Compute Maximum Power
param theta_ja := (theta_jc + theta_ca)*(theta_jb + theta_ba)/(theta_jc + theta_ca + theta_jb + theta_ba);
param delta_T := T_j_max - T_ambient;
param P_max := delta_T / theta_ja;

# area of each components
param component_areas {i in Components}; 

# power of each components
param component_powers {i in Components};

param voltage;
param current_per_bump;
param mc_bump_count;
param io_bump_count;
param bump_pitch;

param package_layer;
param link_pitch;
param wires_per_mc;

# Decision Variable: the number of each components
# Should be integer.
var component_counts {i in Components} integer;

minimize A_die: sum {i in Components} component_counts[i] * component_areas[i];

# Must have at least one of each component.
s.t. range {i in Components}: component_counts[i] >= 1;

s.t. power_constraint: sum {i in Components} component_counts[i] * component_powers[i] <= P_max;
s.t. bump_constraint: sum {i in Components} component_counts[i] * component_areas[i] >= 
bump_pitch * bump_pitch * ((sum {i in Components} component_counts[i] * component_powers[i])/voltage/current_per_bump*2 + mc_bump_count + io_bump_count);

s.t. wire_constraint: sqrt((sum {i in Components} component_counts[i] * component_areas[i]) / 6) * 6 * package_layer / link_pitch >= 
component_counts['mc'] * wires_per_mc;

