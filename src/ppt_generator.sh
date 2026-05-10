#!/usr/bin/env bash

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load environment variables from .env
if [[ -f "$SCRIPT_DIR/.env" ]]; then
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

INPUT_PDF=""
HTML_OUTPUT="output/presentation.html"
PDF_OUTPUT="output/generated_presentation.pdf"
TEMP_IMAGE_FOLDER="temp_images"
TEMP_TABLE_FOLDER="temp_tables"

usage() {
    echo "Usage:"
    echo "  ./run.sh --input <pdf>"
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            INPUT_PDF="$2"
            shift 2
            ;;
        --html-output)
            HTML_OUTPUT="$2"
            shift 2
            ;;
        --pdf-output)
            PDF_OUTPUT="$2"
            shift 2
            ;;
        --temp-image-folder)
            TEMP_IMAGE_FOLDER="$2"
            shift 2
            ;;
        --temp-table-folder)
            TEMP_TABLE_FOLDER="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            usage
            ;;
    esac
done

if [[ -z "$INPUT_PDF" ]]; then
    echo "ERROR: --input is required"
    usage
fi

if [[ -z "$OPENAI_API_KEY" ]]; then
    echo "ERROR: OPENAI_API_KEY not found in environment or .env"
    exit 1
fi

python3 "$SCRIPT_DIR/main.py" \
    --input "$INPUT_PDF" \
    --html-output "$HTML_OUTPUT" \
    --pdf-output "$PDF_OUTPUT" \
    --temp-image-folder "$TEMP_IMAGE_FOLDER" \
    --temp-table-folder "$TEMP_TABLE_FOLDER"