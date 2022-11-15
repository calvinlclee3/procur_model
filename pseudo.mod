param l3_capacity; # per L3 cache, 2MB / mm^2
param l3_bw;       # per L3 cache, previously l3_count_weight
param mc_bw;       # per mem controller, previously mc_count_weight
param working_set_size; # working set size of a given kernel/application

if(working_set_size / (l3_capacity * component_counts['l3']) <= 1):
    l3_hit_rate = ideal_l3_hit_rate;
else # working set size is too large for the cache
    # Suppose the working set size is twice the total L3 capacity, then the hit rate is cut by half from the ideal hit rate.
    l3_hit_rate = ((l3_capacity * component_counts['l3']) / working_set_size) * ideal_l3_hit_rate;

var peak_bw; # effective memory bandwidth available to the core

s.t. constraint: peak_bw <= l3_bw * component_counts['l3'] * l3_hit_rate;
s.t. constraint: peak_bw <= mc_bw * component_counts['mc'] * l3_miss_rate;

