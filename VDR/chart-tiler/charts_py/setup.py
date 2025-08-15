from setuptools import setup
from pybind11.setup_helpers import Pybind11Extension, build_ext

ext_modules = [
    Pybind11Extension(
        "charts_py._core",
        ["src/bindings.cpp"],
        include_dirs=["../../opencpn-libs/include"],
        libraries=["charts"],
        library_dirs=["../../opencpn-libs/build"],
        runtime_library_dirs=["../../opencpn-libs/build"],
    ),
]

setup(
    name="charts_py",
    version="0.0.1",
    packages=["charts_py"],
    package_dir={"": "src"},
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
