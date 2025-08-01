#!/bin/bash
python -m pip install --upgrade pip
pip install --no-cache-dir --only-binary :all: -r requirements.txt
