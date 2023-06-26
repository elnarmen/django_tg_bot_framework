#!/bin/sh
# Script to run linters from IDE
cat $1 | docker compose run -T --rm py-linters flake8 -
