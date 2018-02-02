#!/bin/bash

set -euo pipefail

readonly SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly BASE_DIR="$( dirname "${SCRIPT_DIR}" )"

print_step() {
    echo ""
    echo "[run.sh] $1"
}

print_step "Running flake8"
flake8 .
print_step "Running isort"
isort --check
print_step "Running pylint"
"${BASE_DIR}/run_pylint.sh"
print_step "Running unit tests with coverage"
coverage run "${BASE_DIR}/run_tests.py"
print_step "Show coverage"
coverage report
