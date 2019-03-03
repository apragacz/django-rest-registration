#!/bin/bash

set -euo pipefail

readonly SCRIPT_NAME="$( basename "${BASH_SOURCE[0]}" )"
readonly SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# shellcheck source=./utils.sh
source "${SCRIPT_DIR}/utils.sh"

WATCH="no"

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -w|--watch)
                WATCH="yes"
                shift
            ;;
            *)
                panic "unknown argument $1"
            ;;
        esac
    done
}

build_docs() {
    cd "${BASE_DIR}"
    python setup.py build_sphinx
}

autobuild_docs_with_watch() {
    cd "${BASE_DIR}"
    sphinx-autobuild --watch "${MODULE_DIR}" --ignore "${DOCS_REFERENCE_DIR}" "${DOCS_SRC_DIR}" "${DOCS_BUILD_DIR}/html"
}

main() {
    parse_args "$@"
    rmdir_if_exists "${DOCS_BUILD_DIR}"
    if [ "${WATCH}" == "yes" ]; then
        autobuild_docs_with_watch
    else
        build_docs
    fi
}

main "$@"

