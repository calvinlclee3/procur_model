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

x = np.array([1, 2, 3, 4, 5])
y1 = 2*x + 1
x2 = np.array([6,7,8,9,10])
y2 = 2**x2 + 1

print(x)

plt.figure(num = 3, figsize=(8, 5))
plt.plot(x, y2,**{'color': 'green', 'marker': 'o'})
plt.plot(x2, y1, 
         color='red',   
         linewidth=1.0,  
         linestyle='--' 
        )

plt.savefig('hello.pdf')
plt.close()