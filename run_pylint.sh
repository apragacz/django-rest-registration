#!/bin/bash

set -euo pipefail

pylint --rcfile=setup.cfg rest_registration -E "$@"
