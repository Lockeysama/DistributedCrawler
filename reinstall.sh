#!/bin/bash

pip uninstall tddc -y
python setup.py sdist
pip install dist/tddc-1.0.tar.gz

