#!/bin/bash
# Run the geoapp on an analysis-only geo bundle (zip with analysis outputs +
# per-sample JSONs, no raw activations) — e.g. a bundle attached to a GitHub
# release. Downloads (if a URL), extracts into out/geo/, and launches the app.
#
# Usage:
#   ./scripts/intertemporal/run_geoapp_bundle.sh <zip-path-or-url>
#
# Example:
#   ./scripts/intertemporal/run_geoapp_bundle.sh \
#     https://github.com/justinshenk/temporal-awareness/releases/download/geo-bundles/investment_geometry_analysis.zip

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BASE_DIR="${GEO_BASE_DIR:-$PROJECT_ROOT/out/geo}"

if [ $# -ne 1 ]; then
    echo "Usage: $0 <zip-path-or-url>" >&2
    exit 1
fi

SOURCE="$1"
mkdir -p "$BASE_DIR"

# Download if the source is a URL
if [[ "$SOURCE" == http://* || "$SOURCE" == https://* ]]; then
    ZIP_PATH="$BASE_DIR/$(basename "$SOURCE")"
    if [ -f "$ZIP_PATH" ]; then
        echo "Using already-downloaded $ZIP_PATH"
    else
        echo "Downloading $SOURCE ..."
        curl -fL --progress-bar -o "$ZIP_PATH" "$SOURCE"
    fi
else
    ZIP_PATH="$SOURCE"
    if [ ! -f "$ZIP_PATH" ]; then
        echo "Error: zip not found: $ZIP_PATH" >&2
        exit 1
    fi
fi

# The bundle contains a single top-level dataset directory (e.g. investment_geometry/)
DATASET=$(unzip -Z1 "$ZIP_PATH" | cut -d/ -f1 | sort -u)
if [ -z "$DATASET" ] || [ "$(echo "$DATASET" | wc -l)" -ne 1 ]; then
    echo "Error: expected a single top-level dataset directory inside $ZIP_PATH, got:" >&2
    echo "$DATASET" >&2
    exit 1
fi

TARGET="$BASE_DIR/$DATASET"
if [ -e "$TARGET" ]; then
    echo "Dataset already present at $TARGET — not overwriting."
    echo "(Delete or rename it first if you want to re-extract the bundle.)"
else
    echo "Extracting $DATASET into $BASE_DIR ..."
    unzip -q "$ZIP_PATH" -d "$BASE_DIR"
fi

exec "$SCRIPT_DIR/run_geoapp.sh" "$DATASET"
