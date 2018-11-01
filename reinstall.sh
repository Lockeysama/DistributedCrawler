#!/bin/bash

pip uninstall tddc -y
python setup.py sdist
pip install dist/tddc-1.1.tar.gz

