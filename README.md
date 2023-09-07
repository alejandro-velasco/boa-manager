# Boa Manager: Server Manager for Boa Client CI Jobs

## Overview

This project is a minimally viable server software designed to be installable via python pip. Once installed, a user can run the `boa-manager` CLI to run a REST API Webserver for creating and scheduling jobs

## Prerequisites

`boa-manager` requires the following to function:
- Python 3.11 or later

## Installation

To install, the package must first be built, then installed via pip.

### Build

Install Python package build tools
```bash
python3 -m pip install --upgrade build
```

Build the Pip Package. The final package will be located under the dist folder
```bash
python3 -m build
```

### Install

To install the locally build pip package, run a pip install on the `whl` file.
```
# set VERSION to the appropriate versioned release
VERSION="0.0.1"
python3 -m pip install --upgrade dist/boa_manager-$VERSION-py3-none-any.whl
```

## Usage

Usage: boa-manager

Runs a webserver, which binds to 0.0.0.0:5000

