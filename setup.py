#!/usr/bin/env python
# pylint: disable=redefined-outer-name,missing-docstring


from os.path import join
import re
import setuptools


def get_version():
    """ Read version from __init__.py file """
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
    author_email="mcol@posteo.net",
    description="Visually-guided reaching task for mice",
    keywords=[],
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://mcol.xyz/code/reach",
    packages=['reach'],
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
    ],
)
