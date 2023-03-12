# def someFunc(input):
#     input['b'] = 4
#     input['a'] = "modified"

# if __name__ == "__main__":
#     dictA = {'a' : 3}
#     someFunc(dictA)
#     print(f'{dictA}')
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

test = [{"a":3, "b":3}, {"a":4, "b":4}]

# def fnc(input):
# 	del input[0]["a"]
# 	return input

# returned = fnc(copy.deepcopy(test))
# print(returned)
# print(test)

# curr = copy.deepcopy([result for result in test if result["a"] == 3])

# print(curr)
# print(test)

# curr[0]["a"] = "MODIFIED"

# print(curr)
# print(test)

def get_theta_ca (P_max):
    temp = (0.2 - (178.5/P_max)) / ((85/P_max) - 2)
    print(math.floor(temp * 100000.0)/100000.0)

get_theta_ca(272.8262948)
get_theta_ca(302.1782948)
get_theta_ca(344.4902948)
get_theta_ca(478.3622948)
get_theta_ca(478.3622948)
get_theta_ca(242.2532948)