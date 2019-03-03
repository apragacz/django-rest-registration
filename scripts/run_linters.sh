#!/bin/bash

set -euo pipefail

readonly SCRIPT_NAME="$( basename "${BASH_SOURCE[0]}" )"
readonly SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# shellcheck source=./utils.sh
source "${SCRIPT_DIR}/utils.sh"

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

main "$@"
