# from setuptools import setup
# from Cython.Build import cythonize

# setup(
#     ext_modules = cythonize("fund.pyx")
# )


""" 
python .\cy_setup.py build_ext --inplace
$ python cy_setup.py build_ext --inplace
Which will leave a file in your local directory called 
helloworld.so in unix or helloworld.pyd in Windows. 
"""

from setuptools import Extension, setup
import os
import numpy as np
from Cython.Build import cythonize

include_dirs = [os.getcwd()]
extensions = [
    Extension(e, [f"{e}.pyx"], include_dirs=include_dirs)
    for e in [
        "fund",
        "noise_trader",
        "trend_follower",
        "value_investor",
        "simulation",
        "population",
        "main",
        "results",
        "asset",
        "investor",
    ]
]

setup(ext_modules=cythonize(extensions, annotate=True), include_dirs=[np.get_include()])
