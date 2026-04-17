#!/usr/bin/env bash
# Render Build Script
set -o errexit

pip install -r requirements.txt
python import_data.py
