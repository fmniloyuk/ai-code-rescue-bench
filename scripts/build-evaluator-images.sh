#!/usr/bin/env sh
set -eu

docker build -f docker/patcher.Dockerfile -t rescuebench/patcher:local .
docker build -f docker/python.Dockerfile -t rescuebench/python:local .
docker build -f docker/node.Dockerfile -t rescuebench/node:local .
docker build -f docker/config.Dockerfile -t rescuebench/config:local .
