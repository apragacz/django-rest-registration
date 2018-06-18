#!/bin/bash

set -euo pipefail

readonly BASE_DIR="$( cd "$( dirname "$( dirname "${BASH_SOURCE[0]}" )" )" && pwd )"
readonly SCRIPT_NAME="$( basename "${BASH_SOURCE[0]}" )"

log() {
    local msg="$1"
    echo "[${SCRIPT_NAME}] ${msg}"
}

main() {
    cd "${BASE_DIR}"

    log "Running flake8"
    flake8

    log "Running isort"
    isort --check --diff

    log "Running pylint"
    ./scripts/run_pylint.sh

    log "All linters finished successully."
}

main
