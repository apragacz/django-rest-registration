# shellcheck shell=bash

# SCRIPT_NAME needs to be defined by parent script.

readonly BASE_DIR="$( cd "$( dirname "$( dirname "${BASH_SOURCE[0]}" )" )" && pwd )"

readonly MODULE_NAME="rest_registration"
readonly MODULE_DIR="${BASE_DIR}/${MODULE_NAME}"
readonly TEST_MODULE_NAME="tests"
readonly TEST_MODULE_DIR="${BASE_DIR}/${TEST_MODULE_NAME}"

readonly DOCS_DIR="${BASE_DIR}/docs"
readonly DOCS_SRC_DIR="${DOCS_DIR}"
readonly DOCS_BUILD_DIR="${DOCS_DIR}/_build"
readonly DOCS_REFERENCE_DIR="${DOCS_DIR}/reference"

readonly DIST_DIR="${BASE_DIR}/dist"
readonly BUILD_DIR="${BASE_DIR}/build"

log() {
    local msg="$1"

    echo "[${SCRIPT_NAME}] ${msg}"
}

panic() {
    local msg="$1"

    log "${msg}"
    log "QUITTING"
    exit 1
}

rmdir_if_exists() {
    local dirpath="$1"

    if [ -d "${dirpath}" ]; then
        rm -rv "${dirpath}"
    fi
}
