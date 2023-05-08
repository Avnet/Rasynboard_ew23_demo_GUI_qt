#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
sudo apt install -y libglib2.0-dev python3-pyqt5
pip3 install -r ${SCRIPT_DIR}/requirements.txt