import setuptools
from os.path import join
import re


def get_version():
    with open(join('reach', '__init__.py'), 'r') as f:
        content = f.read()
    p = re.compile(r'^__version__ = [\'"]([^\'\"]*)[\'"]', re.M)
    return p.search(content).group(1)


with open("readme.rst", "r") as f:
    long_description = f.read()


setuptools.setup(
    name="reach",
    version=get_version(),
    author="Matt Colligan",
    author_email="matt.colligan@ed.ac.uk",
    description="Visually-guided reaching task for mice",
    keywords=[],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/DuguidLab/reach",
    packages=setuptools.find_packages(),
    install_requires=[
        "matplotlib",
        "seaborn",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
    ],
)
