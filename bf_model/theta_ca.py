import math

def get_theta_ca (P_max):
    temp = (0.2 - (178.5/P_max)) / ((85/P_max) - 2)
    print(math.floor(temp * 100000.0)/100000.0)


get_theta_ca(317.52000000000004)

