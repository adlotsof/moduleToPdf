#!/bin/bash
sudo apt-get install wkhtmltopdf || exit 1
python3 -m venv venv || exit 1
source venv/bin/activate || exit 1
pip3 install -r requirements.txt || exit 1
