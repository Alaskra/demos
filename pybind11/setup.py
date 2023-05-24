from setuptools import setup, Extension
import pybind11

functions_module = Extension(
    name='example',
    sources=['example.cpp'],
    extra_compile_args=["-O3","-fPIC"],
    include_dirs=[pybind11.get_include()],
)

setup(ext_modules=[functions_module])
