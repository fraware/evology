from setuptools import Extension, setup
import os

from Cython.Build import cythonize

include_dirs = [os.getcwd()]
extensions = [
    Extension(e, [f"{e}.pyx"], include_dirs=include_dirs)
    for e in [
        "fund",
    ]
]

setup(
    ext_modules=cythonize(extensions, annotate=True),
    # include_dirs=[numpy.get_include()],
)
