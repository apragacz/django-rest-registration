#!/bin/bash

set -euo pipefail

readonly BASE_DIR="$( cd "$( dirname "$( dirname "${BASH_SOURCE[0]}" )" )" && pwd )"

cd "${BASE_DIR}"
pylint --rcfile=setup.cfg rest_registration tests -E "$@"
