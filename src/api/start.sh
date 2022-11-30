#!/bin/bash
ROOT_DIR=$(git rev-parse --show-toplevel)
flask -A "${ROOT_DIR}/src/api.py" --debug run
