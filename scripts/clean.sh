#!/bin/bash

set -euo pipefail

readonly SCRIPT_NAME="$( basename "${BASH_SOURCE[0]}" )"
readonly SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# shellcheck source=./utils.sh
source "${SCRIPT_DIR}/utils.sh"

main() {
    log "Cleaning up tox"
    rm -rfv "${BASE_DIR}/.tox"

    log "Cleaning up pytest cache"
    rm -rfv "${BASE_DIR}/.pytest_cache"

    log "Cleaning up pycache files"
    find "${BASE_DIR}" -iname '__pycache__' -type d -print0 | xargs -0 rm -rfv

    log "Cleaning up test results"
    rm -fv "${BASE_DIR}/TEST-*.xml"

    log "Cleaning up coverage files"
    rm -fv "${BASE_DIR}/.coverage"
    rm -fv "${BASE_DIR}/coverage.xml"
    rm -rfv "${BASE_DIR}/coverage_html_report"

    log "Cleaning up dist packages"
    rm -rfv "${DIST_DIR}"

    log "Cleaning up build packages"
    rm -rfv "${BUILD_DIR}"

    log "Cleaning up built docs"
    rm -rfv "${DOCS_BUILD_DIR}"
}

main "$@"
