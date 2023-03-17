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

# def lol(input):
#     input[0]["b"] = "CHANGED"

# print(test)
# lol(test)
# print(test)

 
# dataset-1
x1 = [89, 43, 36, 36, 95, 10,
      66, 34, 38, 20]
 
y1 = [21, 46, 3, 35, 67, 95,
      53, 72, 58, 10]
 
# dataset2
x2 = [26, 29, 48, 64, 6, 5,
      36, 66, 72, 40]
 
y2 = [26, 34, 90, 33, 38,
      20, 56, 2, 47, 15]
 
plt.scatter(x1, y1, c ="pink",
            linewidths = 2,
            marker ="s",
            edgecolor ="green",
            s = 50,
            label="LABEL1")
 
plt.scatter(x2, y2, c ="yellow",
            linewidths = 2,
            marker ="^",
            edgecolor ="red",
            s = 200,
            label="LABEL2")
 
plt.xlabel("X-axis")
plt.ylabel("Y-axis")
plt.legend()

plt.savefig(f'TEST.pdf')
plt.close()