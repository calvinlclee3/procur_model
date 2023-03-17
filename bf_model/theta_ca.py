import math

def get_theta_ca (P_max):
    temp = (0.2 - (178.5/P_max)) / ((85/P_max) - 2)
    print(math.floor(temp * 100000.0)/100000.0)

get_theta_ca(248.6582948)
get_theta_ca(260.5382948)
get_theta_ca(303.01829480000004)
get_theta_ca(336.49829480000005)
get_theta_ca(336.49829480000005)
get_theta_ca(262.5394148)




