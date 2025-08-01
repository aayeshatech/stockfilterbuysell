#!/bin/bash
# Prevent unnecessary operations
export PIP_NO_CACHE_DIR=yes
export PIP_DISABLE_PIP_VERSION_CHECK=1

# Stable installation order
python -m pip install --upgrade "pip<24.1"  # Lock pip version
pip install --ignore-installed -r requirements.txt
