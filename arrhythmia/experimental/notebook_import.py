"""
Work-around to integrate project structure into jupyter notebooks.
Adds root project directory into module search path.
"""

import sys
import os

module_path = os.path.abspath(os.path.join(os.pardir, os.pardir))
if module_path not in sys.path:
    sys.path.append(module_path)

# Environment variable PYTHONHASHSEED=0 must be set for reproducing the results
if os.environ['PYTHONHASHSEED'] != '0':
    print('WARNING! Environment variable PYTHONHASHSEED=0 must be set for reproducing the results.')

# Seed random number generators for results reproduction
import random
random.seed(2)
from numpy.random import seed
seed(1)
from tensorflow import set_random_seed
set_random_seed(2)
