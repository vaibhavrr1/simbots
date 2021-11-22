from setuptools import setup,find_packages
import io

def read_file(filepath):
    ''' read the file '''
    with io.open(filepath, 'r') as filepointer:
        res = filepointer.read()
    return res

setup(
    name = "simbots",
    version = "0.0.10",
    description = "Simple bots or Simbots is a library designed to create simple bots using the power of python.",
    packages =["simbots"],
    package_dir = {'':'simbots'},
    classifiers = ["Development Status :: 1 - Planning","Operating System :: OS Independent","License :: OSI Approved :: MIT License","Programming Language :: Python :: 3"],
    install_requires =['sklearn','objectpath'],
    license_files = ('LICENSE.txt'),
   long_description = read_file('README.md'),


)