#!/usr/bin/env python3

import subprocess
from setuptools import find_packages, setup

spacyfishing_version = subprocess.run(['git', 'describe', '--tags'], stdout=subprocess.PIPE).stdout.decode("utf-8").strip()

with open("README.md", "r") as fh:
    long_description = fh.read()


CLASSIFIERS = [
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]

setup(
    name="spacyfishing",
    version=spacyfishing_version,
    author="Lucas Terriel",
    license="MIT",
    description="A spaCy wrapper of Entity-Fishing (component) for named entity disambiguation and linking on Wikidata.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Lucaterre/spacyfishing",
    install_requires=['spacy>=3.3.1', 'requests>=2.28.0'],
    packages=find_packages("spacyfishing"),
    classifiers=CLASSIFIERS,
    python_requires='>=3.8',
    entry_points={
        'spacy_factories': 'entityfishing = spacyfishing.entity_fishing_linker:EntityFishing'
    },
    keywords=["spacy-extension", "entity linking", "entity disambiguation", "nlp", "natural language processing", "entity-fishing"]
)