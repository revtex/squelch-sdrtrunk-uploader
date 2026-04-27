FROM mcr.microsoft.com/devcontainers/java:1-21-bookworm

# Gradle is provided by gradle/actions/setup-gradle in CI; locally we let the
# project's gradle wrapper download a pinned version on first build. The base
# image already has JDK 21 (Temurin) on PATH.

USER root
RUN apt-get update && apt-get install -y --no-install-recommends \
        python3 python3-venv python3-pip python3-dev \
        ripgrep jq \
        ca-certificates curl gnupg \
    && rm -rf /var/lib/apt/lists/*

# GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
        | gpg --dearmor -o /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
        > /etc/apt/sources.list.d/github-cli.list \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

USER vscode
