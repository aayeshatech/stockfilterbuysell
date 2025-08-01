#!/bin/bash
# Force pre-built wheels and skip unnecessary operations
export PIP_NO_CACHE_DIR=yes
export PIP_DISABLE_PIP_VERSION_CHECK=1

# Install in optimal order
python -m pip install --upgrade "pip<24.1"
pip install --only-binary :all: --ignore-installed -r requirements.txt
