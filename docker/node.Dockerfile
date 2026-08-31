FROM node:22-bookworm-slim

ARG TYPESCRIPT_VERSION=5.9.2
ARG ESLINT_VERSION=9.34.0

RUN npm install --global --omit=optional \
    "typescript@${TYPESCRIPT_VERSION}" \
    "eslint@${ESLINT_VERSION}" \
    "tsx@4.20.5" \
    "@typescript-eslint/parser@8.41.0" \
    "@typescript-eslint/eslint-plugin@8.41.0" \
    "react@19.1.1" \
    "react-dom@19.1.1" \
    "react-test-renderer@19.1.1"

ENV NODE_PATH=/usr/local/lib/node_modules
WORKDIR /workspace
