#!/bin/bash

readonly BASE_DIR="$( cd "$( dirname "$( dirname "${BASH_SOURCE[0]}" )" )" && pwd )"

set -euo pipefail

cd "${BASE_DIR}"
rm -fv TEST-*.xml
rm -fv .coverage
rm -fv coverage.xml
rm -rfv dist/
rm -rfv docs/_build
