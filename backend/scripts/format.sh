#!/bin/sh -e
set -x
poetry run ruff check lambdas shared openapi scripts --fix
poetry run ruff format lambdas shared openapi scripts scripts