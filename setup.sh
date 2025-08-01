#!/bin/bash
# Prevent conflicts by isolating installations
python -m pip install --user --upgrade pip
python -m pip install --user -r requirements.txt --no-deps
mkdir -p ephe
