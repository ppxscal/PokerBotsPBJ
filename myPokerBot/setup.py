from setuptools import setup
from Cython.Build import cythonize

setup(
    name="Monte Carlo", ext_modules=cythonize("monteCarlo.pyx"), zip_safe=False,
)

# python setup.py build_ext --inplace

