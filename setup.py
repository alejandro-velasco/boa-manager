from setuptools import setup

with open(f"requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    install_requires=requirements,
    entry_points = {
        'console_scripts': ['boa-manager=boa_manager.boa_manager:entrypoint']
    }
)