#!/usr/bin/python3
import os
from setuptools import setup

curdir=os.path.abspath(os.path.dirname(__file__))

#with open(os.path.join(curdir,"README.md")) as f:
#	README=f.read()

setup(
    name="easyaudi",
    version="0.0.0",
    description="Uses the commoncodes standard to create more specific Exceptions",
#    long_description=README,
#    long_description_content_type="text/markdown",
    url="https://github.com/RiedleroD/easyaudi",
    author="Riedler",
    author_email="riedler@gelse.net",
    license="Creative Commons BY-SA 4.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["easyaudi"],
    include_package_data=True,
    install_requires=[],
    entry_points={'console_scripts': ['easyaudi = easyaudi.__main__:main']},
)
