#!/bin/bash

set -euo pipefail

readonly BASE_DIR="$( cd "$( dirname "$( dirname "${BASH_SOURCE[0]}" )" )" && pwd )"

cd "${BASE_DIR}"
rm -rf dist
python setup.py sdist
python setup.py bdist_wheel
twine upload dist/*

