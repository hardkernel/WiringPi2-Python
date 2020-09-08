#!/usr/bin/env python

import os
import sys

from setuptools import setup, Extension
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist
from distutils.spawn import find_executable
from glob import glob

sources = glob('WiringPi/devLib/*.c')
sources += glob('WiringPi/wiringPi/*.c')

# Exclude template file.
sources = list(set(sources) - set(glob('WiringPi/wiringPi/odroid_template.c')))

# If we have swig, use it.  Otherwise, use the pre-generated
# wrapper from the source distribution.
if find_executable('swig'):
    sources += ['wiringpi.i']
elif os.path.exists('wiringpi_wrap.c'):
    sources += ['wiringpi_wrap.c']
else:
    print("Error:  Building this module requires either that swig is installed\n"
          "        (e.g., 'sudo apt install swig') or that wiringpi_wrap.c from the\n"
          "        source distribution (on pypi) is available.")
    sys.exit(1)

try:
    sources.remove('WiringPi/devLib/piFaceOld.c')
except ValueError:
    # the file is already excluded in the source distribution
    pass


# Fix so that build_ext runs before build_py
# Without this, wiringpi.py is generated too late and doesn't
# end up in the distribution when running setup.py bdist or bdist_wheel.
# Based on:
#  https://stackoverflow.com/a/29551581/7938656
#  and
#  https://blog.niteoweb.com/setuptools-run-custom-code-in-setup-py/
class build_py_ext_first(build_py):
    def run(self):
        self.run_command("build_ext")
        return build_py.run(self)


# Make sure wiringpi_wrap.c is available for the source dist, also.
class sdist_ext_first(sdist):
    def run(self):
        self.run_command("build_ext")
        return sdist.run(self)


_odroid_wiringpi = Extension(
    '_odroid_wiringpi',
    include_dirs=['WiringPi/wiringPi','WiringPi/devLib'],
    sources=sources,
    swig_opts=['-threads'],
    extra_link_args=['-lcrypt', '-lrt'],
)

setup(
    name = 'odroid_wiringpi',
    version = '3.7',
    ext_modules = [ _odroid_wiringpi ],
    py_modules = ["odroid_wiringpi"],
    install_requires=[],
    cmdclass = {'build_py' : build_py_ext_first, 'sdist' : sdist_ext_first},
)
