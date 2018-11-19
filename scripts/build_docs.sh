#!/bin/bash

set -euo pipefail

readonly BASE_DIR="$( cd "$( dirname "$( dirname "${BASH_SOURCE[0]}" )" )" && pwd )"
readonly DOCS_BUILD_DIR="${BASE_DIR}/docs/_build"

rmdir_if_exists() {
    local dirpath="$1"

    if [ -d "${dirpath}" ]; then
        rm -rv "${dirpath}"
    fi
}


main() {
    rmdir_if_exists "${DOCS_BUILD_DIR}"
    cd "${BASE_DIR}"
    python setup.py build_sphinx
}

main "$@"

