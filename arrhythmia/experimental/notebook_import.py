"""
Work-around to integrate project structure into jupyter notebooks.
Adds root project directory into module search path.
"""

import sys
import os

module_path = os.path.abspath(os.path.join(os.pardir, os.pardir))
if module_path not in sys.path:
    sys.path.append(module_path)
