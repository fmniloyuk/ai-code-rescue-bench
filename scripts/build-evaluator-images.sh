#!/usr/bin/env sh
set -eu

docker build -f docker/python.Dockerfile -t rescuebench/python:local .
docker build -f docker/node.Dockerfile -t rescuebench/node:local .
docker build -f docker/config.Dockerfile -t rescuebench/config:local .
docker pull alpine/git:2.47.2
