#!/bin/bash
# download_model.sh - Scarica un modello da un URL e verifica il checksum SHA256
#
# Uso: ./download_model.sh <URL> <SHA256_EXPECTED>
#
# Esempio: ./download_model.sh https://example.com/model.gguf a1b2c3d4...

set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <URL> <SHA256_EXPECTED>" >&2
    exit 1
fi

URL="$1"
EXPECTED_SHA256="$2"

# Directory dove salvare il file (relativa alla posizione dello script)
DOWNLOAD_DIR="./downloads"
mkdir -p "$DOWNLOAD_DIR"

# Nome file estratto dall'URL (rimuove query e fragment)
FILENAME=$(basename "$URL" | cut -d'?' -f1 | cut -d'#' -f1)
if [[ -z "$FILENAME" ]]; then
    echo "Error: Unable to determine filename from URL" >&2
    exit 1
fi

DOWNLOAD_PATH="$DOWNLOAD_DIR/$FILENAME"

echo "Downloading $URL to $DOWNLOAD_PATH..."

# Download con curl (fallback a wget se curl non disponibile)
if command -v curl >/dev/null 2>&1; then
    curl -L --fail --silent --show-error --output "$DOWNLOAD_PATH" "$URL"
elif command -v wget >/dev/null 2>&1; then
    wget --quiet --output-document="$DOWNLOAD_PATH" "$URL"
else
    echo "Error: Neither curl nor wget is available" >&2
    exit 1
fi

# Calcola SHA256
CALCULATED_SHA256=$(sha256sum "$DOWNLOAD_PATH" | awk '{print $1}')

echo "Expected SHA256: $EXPECTED_SHA256"
echo "Calculated SHA256: $CALCULATED_SHA256"

if [[ "$CALCULATED_SHA256" == "$EXPECTED_SHA256" ]]; then
    echo "Checksum OK. File saved to $DOWNLOAD_PATH"
    exit 0
else
    echo "Error: Checksum mismatch!" >&2
    rm -f "$DOWNLOAD_PATH"
    exit 1
fi