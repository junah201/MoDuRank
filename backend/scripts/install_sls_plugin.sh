#!/bin/sh -e
set -x
serverless plugin install --name serverless-python-requirements
serverless plugin install --name serverless-dotenv-plugin