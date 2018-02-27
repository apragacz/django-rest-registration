#!/bin/bash

set -euo pipefail

readonly SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly BASE_DIR="$( dirname "${SCRIPT_DIR}" )"

print_step() {
    echo ""
    echo "[run.sh] $1"
}

main() {
    local codecov_token="${CODECOV_TOKEN:-}"
    print_step "Running flake8"
    flake8 .
    print_step "Running isort"
    isort --check
    print_step "Running pylint"
    "${BASE_DIR}/run_pylint.sh"
    print_step "Running unit tests with coverage"
    coverage run "${BASE_DIR}/run_tests.py"
    if [ -n "${codecov_token}" ]; then
        print_step "Generating coverage XML"
        coverage xml
        print_step "Sending coverage to codecov.io"
        codecov
    else
        print_step "Showing coverage"
        coverage report
    fi
}

main
