#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
sudo rm -rf ${SCRIPT_DIR}/__pycache__
${SCRIPT_DIR}/rasynvoice.py $@