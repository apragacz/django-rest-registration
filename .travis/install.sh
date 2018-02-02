#!/bin/bash

set -euo pipefail

readonly SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
readonly BASE_DIR="$( dirname "${SCRIPT_DIR}" )"
readonly DJANGO_VERSION="${DJANGO_VERSION:-}"

print_step() {
    echo ""
    echo "[install.sh] $1"
}

if [ -n "${DJANGO_VERSION}" ]; then
    print_step "Installing Django ${DJANGO_VERSION}"
    pip install "django==${DJANGO_VERSION}"
fi

print_step "Installing base requirements"
pip install -r "${BASE_DIR}/requirements.txt"
print_step "Installing test requirements"
pip install -r "${BASE_DIR}/tests/requirements.txt"
