import math

def get_theta_ca (P_max):
    temp = (0.2 - (178.5/P_max)) / ((85/P_max) - 2)
    print(math.floor(temp * 100000.0)/100000.0)

get_theta_ca(272.8262948)
get_theta_ca(302.1782948)
get_theta_ca(344.4902948)
get_theta_ca(478.3622948)
get_theta_ca(478.3622948)
get_theta_ca(242.2532948)