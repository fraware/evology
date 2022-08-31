# from setuptools import setup
# from Cython.Build import cythonize

# setup(
#     ext_modules = cythonize("fund.pyx")
# )


""" 
python .\setup.py build_ext --inplace
$ python setup.py build_ext --inplace
Which will leave a file in your local directory called 
helloworld.so in unix or helloworld.pyd in Windows. 
"""

from setuptools import Extension, setup
import os

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
        
    ]
]

setup(
    ext_modules=cythonize(extensions, annotate=True),
    # include_dirs=[numpy.get_include()],
)
