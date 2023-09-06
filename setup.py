from setuptools import setup

with open(f"requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    install_requires=requirements
)