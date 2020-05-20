SHELL := /bin/bash

PACKAGE_DIR := rest_registration
TESTS_DIR := tests
DIST_DIR := dist
BUILD_DIR := build
DOCS_DIR := docs
DOCS_SRC_DIR := ${DOCS_DIR}
DOCS_BUILD_DIR := "${DOCS_DIR}/_build"
DOCS_REFERENCE_DIR := "${DOCS_DIR}/reference"

GREP := grep
AWK := awk
SORT := sort
RM := rm
FIND := find
XARGS := xargs
CAT := cat

PYTHON := python
FLAKE8 := flake8
FLAKE8_OPTS :=
MYPY := mypy
MYPY_OPTS :=
PYLINT := pylint
PYLINT_OPTS := --rcfile=setup.cfg
PYTEST := py.test
PYTEST_OPTS :=
TWINE := twine
SPHINXBUILD := sphinx-build
SPHINXBUILD_OPTS :=
SPHINXBUILD_WARNING_LOG = sphinx-warnings.log
SPHINXAUTOBUILD := sphinx-autobuild
SPHINXAUTOBUILD_OPTS := --watch ${PACKAGE_DIR} --ignore ${DOCS_REFERENCE_DIR}

.PHONY: all
all: check test build check_package  ## check code, test, build, check package

.PHONY: install_dev
install_dev:  ## install all pip requirements and the package as editable
	${PYTHON} -m pip install -r requirements/requirements-all.txt ${ARGS}
	${PYTHON} -m pip install -e .

.PHONY: test
test:  ## run tests
	${PYTEST} ${PYTEST_OPTS} ${ARGS}

.PHONY: check
check: flake8 mypy pylint check_docs  ## run checks: flake8, mypy, pylint, check_docs

.PHONY: flake8
flake8:  ## run flake8
	${FLAKE8} ${FLAKE8_OPTS} ${ARGS}

.PHONY: mypy
mypy:  ## run mypy
	${MYPY} ${MYPY_OPTS} ${PACKAGE_DIR} ${ARGS}

.PHONY: pylint
pylint:  ## run pylint
# run pylint for production code and test code separately
	${PYLINT} ${PYLINT_OPTS} ${PACKAGE_DIR} ${DOCS_DIR} ./*.py ${ARGS}
	${PYLINT} ${PYLINT_OPTS} --disable=duplicate-code --disable=redefined-outer-name --disable=too-many-arguments ${TESTS_DIR} ${ARGS}

.PHONY: upload_package
upload_package: build_package check_package  ## upload the package to PyPI
	${TWINE} upload ${DIST_DIR}/*

.PHONY: check_package
check_package: build_package  ## check that the built package is well-formed
	${TWINE} check ${DIST_DIR}/*

.PHONY: build
build: build_package  ## alias for build_package

.PHONY: build_package
build_package:  ## build package (source + wheel)
	-${RM} -r ${DIST_DIR}
	${PYTHON} setup.py sdist
	${PYTHON} setup.py bdist_wheel

.PHONY: build_docs
build_docs:  ## build documentation
	${SPHINXBUILD} ${SPHINXBUILD_OPTS} ${DOCS_SRC_DIR} ${DOCS_BUILD_DIR}/html ${ARGS}

.PHONY: check_docs
check_docs:  ## check that the docs do not contain any warnings / errors
	${SPHINXBUILD} ${SPHINXBUILD_OPTS} ${DOCS_SRC_DIR} ${DOCS_BUILD_DIR}/html -w ${SPHINXBUILD_WARNING_LOG} ${ARGS}
	${CAT} ${SPHINXBUILD_WARNING_LOG}
	@${SHELL} -c '[ ! -s ${SPHINXBUILD_WARNING_LOG} ]'

.PHONY: watch_docs
watch_docs:  ## build documentation in watch mode (will start additonal http server)
	${SPHINXAUTOBUILD} ${SPHINXAUTOBUILD_OPTS} ${DOCS_SRC_DIR} ${DOCS_BUILD_DIR}/html ${ARGS}

.PHONY: clean
clean:  ## remove generated files
	-${RM} -r .tox
	-${RM} -r .pytest_cache
	-${RM} -r .mypy_cache

	${FIND} "." -iname '__pycache__' -type d -print0 | ${XARGS} -0 ${RM} -r

	-${RM} TEST-*.xml

	-${RM} .coverage
	-${RM} coverage.xml
	-${RM} -r coverage_html_report

	-${RM} -r ${DIST_DIR}
	-${RM} -r ${BUILD_DIR}
	-${RM} -r ${DOCS_BUILD_DIR}

.PHONY: help
help:  ## list all make targets
	@${AWK} -F ':.*##' '$$0 ~ FS {printf "%-32s%s\n", $$1 ":", $$2}' $(MAKEFILE_LIST) | ${GREP} -v {AWK} | ${SORT}
