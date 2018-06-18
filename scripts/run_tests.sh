#!/bin/bash

set -euo pipefail

readonly BASE_DIR="$( cd "$( dirname "$( dirname "${BASH_SOURCE[0]}" )" )" && pwd )"

PYTHONPATH="${BASE_DIR}" py.test "$@"
