#!/usr/bin/env python

from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='erdkeys',
    version='0.1.3',
    author='Flying Stone',
    description='Tools for working with elrond pem files and json keystores',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/flyingbasalt/erdkeys',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        'Operating System :: POSIX',
    ],
    scripts =['erdkeys/pem2json.py', 'erdkeys/json2pem.py'], 
    python_requires='>=3.6',
    install_requires=['cryptography', 'bech32'],
)

