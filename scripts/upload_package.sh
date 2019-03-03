#!/bin/bash

set -euo pipefail

readonly SCRIPT_NAME="$( basename "${BASH_SOURCE[0]}" )"
readonly SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# shellcheck source=./utils.sh
source "${SCRIPT_DIR}/utils.sh"

main() {
    log "Cleaning up dist directory"
    rm -rf "${DIST_DIR}"

    log "Building sdist/bdist_wheel packages"
    cd "${BASE_DIR}"
    python setup.py sdist
    python setup.py bdist_wheel

    log "Uploading built packages"
    twine upload "${DIST_DIR}/*"
}

main "$@"

