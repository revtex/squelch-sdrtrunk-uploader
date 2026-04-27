#!/usr/bin/env bash
# Post-create hook for the Squelch SDRTrunk uploader devcontainer.
# Runs once per container creation. Idempotent.
set -euo pipefail

cd "$(dirname "$0")/.."

echo ">> Configuring Python venv for shim/"
if [[ ! -d shim/.venv ]]; then
    python3 -m venv shim/.venv
fi
# shellcheck disable=SC1091
source shim/.venv/bin/activate
pip install --upgrade pip --quiet
pip install -e "shim[dev]" --quiet

echo ">> Pre-warming Gradle (downloads wrapper + dependencies)"
if [[ -f plugin/gradlew ]]; then
    (cd plugin && ./gradlew --no-daemon help >/dev/null) || \
        echo "   (gradle warm-up failed — re-run after editing build.gradle.kts)"
else
    echo "   (gradle wrapper not yet generated — skipping warm-up)"
fi

echo ">> Devcontainer ready."
echo "   - Java plugin:  cd plugin && ./gradlew test"
echo "   - Python:       source shim/.venv/bin/activate && pytest -q"
