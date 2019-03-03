#!/bin/bash

set -euo pipefail

readonly SCRIPT_NAME="$( basename "${BASH_SOURCE[0]}" )"
readonly SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# shellcheck source=./utils.sh
source "${SCRIPT_DIR}/utils.sh"

main() {
    cd "${BASE_DIR}"
    pylint --rcfile=setup.cfg "${MODULE_NAME}" "${TEST_MODULE_NAME}" -E "$@"
}

main "$@"
