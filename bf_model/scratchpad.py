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

test = [{"a":3, "b":3}, {"c":4, "d":4}]

def fnc(input):
	del input[0]["a"]
	return input

returned = fnc(copy.deepcopy(test))
print(returned)
print(test)