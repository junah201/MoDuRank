#!/bin/sh -e
set -x
poetry run ruff check lambdas shared scripts --fix
poetry ruff format lambdas shared scripts scripts