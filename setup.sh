#!/bin/bash
# Prevent unnecessary reinstalls
export PIP_NO_CACHE_DIR=true
export PIP_DISABLE_PIP_VERSION_CHECK=1

# Install in optimal order
pip install --upgrade pip==24.0  # Lock pip version
pip install --no-build-isolation -r requirements.txt
