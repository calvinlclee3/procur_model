import math

def get_theta_ca (P_max):
    temp = (0.2 - (178.5/P_max)) / ((85/P_max) - 2)
    print(math.floor(temp * 100000.0)/100000.0)


get_theta_ca(340.1029008402501)
get_theta_ca(347.8429008402501)
get_theta_ca(351.98290084025007)
get_theta_ca(365.6629008402501)
get_theta_ca(394.4629008402501)
get_theta_ca(429.38290084025004)
get_theta_ca(422.1429008402501)
get_theta_ca(427.9429008402501)
get_theta_ca(479.6029008402501)
get_theta_ca(353.9840208402501)
