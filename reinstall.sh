#!/bin/bash

pip uninstall tddc -y
python setup.py sdist
pip install dist/tddc-3.0.tar.gz

