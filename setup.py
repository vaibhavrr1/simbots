from setuptools import setup


from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name = "simbots",
    version = "0.0.20",
    description = "Simple bots or Simbots is a library designed to create simple bots using the power of python.",
    packages =["simbots","simbots\\utils"],
    package_dir = {'':'simbots'},
    classifiers = ["Development Status :: 1 - Planning","Operating System :: OS Independent","License :: OSI Approved :: MIT License","Programming Language :: Python :: 3"],
    install_requires =['sklearn','objectpath'],
    license_files = ('LICENSE.txt'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    author = "Vaibhav Arora",
    author_email ="vaibhav.rr1@gmail.com"


)