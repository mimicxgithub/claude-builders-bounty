#!/usr/bin/env bash
# ==============================================================================
# Git Changelog Generator
# Automatically categorizes commits into Added/Fixed/Changed/Removed
# Acceptance Criteria: Works via bash changelog.sh
# ==============================================================================

set -euo pipefail

OUTPUT_FILE="${1:-CHANGELOG.md}"
VERSION_NAME="${2:-Unreleased}"
DATE_STR=$(date -u +"%Y-%m-%d")

# Detect latest git tag
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

if [ -n "$LATEST_TAG" ]; then
    echo "[INFO] Generating changelog since tag: $LATEST_TAG"
    COMMITS_RANGE="$LATEST_TAG..HEAD"
else
    echo "[INFO] No tags found. Generating changelog from full repository history."
    COMMITS_RANGE="HEAD"
fi

TEMP_ADDED=$(mktemp)
TEMP_FIXED=$(mktemp)
TEMP_CHANGED=$(mktemp)
TEMP_REMOVED=$(mktemp)

trap 'rm -f "$TEMP_ADDED" "$TEMP_FIXED" "$TEMP_CHANGED" "$TEMP_REMOVED"' EXIT

# Read git log
git log "$COMMITS_RANGE" --format="%h|%an|%s" | while IFS='|' read -r hash author subject; do
    lower=$(echo "$subject" | tr '[:upper:]' '[:lower:]')
    entry="- $subject (\`$hash\`) - @$author"

    if [[ "$lower" =~ ^(feat|feature|add|new|create) ]]; then
        echo "$entry" >> "$TEMP_ADDED"
    elif [[ "$lower" =~ ^(fix|bug|patch|resolve|hotfix) ]]; then
        echo "$entry" >> "$TEMP_FIXED"
    elif [[ "$lower" =~ ^(remove|delete|drop|deprecate) ]]; then
        echo "$entry" >> "$TEMP_REMOVED"
    else
        echo "$entry" >> "$TEMP_CHANGED"
    fi
done

# Assemble CHANGELOG.md
cat <<EOF > "$OUTPUT_FILE"
# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [$VERSION_NAME] - $DATE_STR
EOF

if [ -s "$TEMP_ADDED" ]; then
    echo -e "\n### Added" >> "$OUTPUT_FILE"
    cat "$TEMP_ADDED" >> "$OUTPUT_FILE"
fi

if [ -s "$TEMP_FIXED" ]; then
    echo -e "\n### Fixed" >> "$OUTPUT_FILE"
    cat "$TEMP_FIXED" >> "$OUTPUT_FILE"
fi

if [ -s "$TEMP_CHANGED" ]; then
    echo -e "\n### Changed" >> "$OUTPUT_FILE"
    cat "$TEMP_CHANGED" >> "$OUTPUT_FILE"
fi

if [ -s "$TEMP_REMOVED" ]; then
    echo -e "\n### Removed" >> "$OUTPUT_FILE"
    cat "$TEMP_REMOVED" >> "$OUTPUT_FILE"
fi

echo "[SUCCESS] Changelog successfully generated at $OUTPUT_FILE"
