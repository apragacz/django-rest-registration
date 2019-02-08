#!/bin/bash

set -euo pipefail

readonly BASE_DIR="$( cd "$( dirname "$( dirname "${BASH_SOURCE[0]}" )" )" && pwd )"
readonly SCRIPT_NAME="$( basename "${BASH_SOURCE[0]}" )"

log() {
    local msg="$1"
    echo "[${SCRIPT_NAME}] ${msg}"
}

main() {
    log "Cleaning up dist directory"
    cd "${BASE_DIR}"
    rm -rf dist

    log "Building sdist/bdist_wheel packages"
    python setup.py sdist
    python setup.py bdist_wheel

    log "Uploading built packages"
    twine upload dist/*
}

main "$@"

