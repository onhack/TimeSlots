# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="timeslots",
    version="0.0.1",
    description="A Python package to generate free slots from a list of events scheduling them in a calendar with business hours. Easy to use.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Geovani Perez França",
    author_email="hi@geovani.dev",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=["timeslots"],
    include_package_data=True,
    install_requires=["python-dateutil", "icalendar"]
)