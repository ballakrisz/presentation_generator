#!/bin/bash

set -e

# ----------------------------------------
# ARGUMENTS
# ----------------------------------------

PDF_PATH=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --input)
            PDF_PATH="$2"
            shift 2
            ;;
        *)
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done

if [[ -z "$PDF_PATH" ]]; then
    echo "ERROR: --input is required"
    exit 1
fi

# ----------------------------------------
# CONFIG
# ----------------------------------------

MODEL_PATH="doclayout_yolo_docstructbench_imgsz1024.pt"

TEMP_DIR=$(mktemp -d)

cleanup() {
    rm -rf "$TEMP_DIR"
}

trap cleanup EXIT

# ----------------------------------------
# CHECK FILES
# ----------------------------------------

if [ ! -f "$PDF_PATH" ]; then
    echo "PDF not found: $PDF_PATH"
    exit 1
fi

if [ ! -f "$MODEL_PATH" ]; then
    echo "Model not found: $MODEL_PATH"
    echo "Download it with:"
    echo "wget https://huggingface.co/juliozhao/DocLayout-YOLO-DocStructBench/resolve/main/doclayout_yolo_docstructbench_imgsz1024.pt"
    exit 1
fi

# ----------------------------------------
# OUTPUT
# ----------------------------------------

PDF_NAME=$(basename "$PDF_PATH" .pdf)

FIGURE_OUTPUT_DIR="figures/$PDF_NAME"
TABLE_OUTPUT_DIR="tables/$PDF_NAME"

rm -rf "$FIGURE_OUTPUT_DIR"
rm -rf "$TABLE_OUTPUT_DIR"

mkdir -p "$FIGURE_OUTPUT_DIR"
mkdir -p "$TABLE_OUTPUT_DIR"

# ----------------------------------------
# CONVERT PDF TO PAGE IMAGES
# ----------------------------------------

echo "Converting PDF pages..."

pdftoppm -png -r 300 "$PDF_PATH" "$TEMP_DIR/page"

echo "PDF converted."

# ----------------------------------------
# RUN PYTHON EXTRACTION
# ----------------------------------------

python3 << EOF

from doclayout_yolo import YOLOv10
import cv2
import glob
import os
import pytesseract
import re
import json

MODEL_PATH = "$MODEL_PATH"

PAGE_PATTERN = "$TEMP_DIR/page-*.png"

FIGURE_OUTPUT_DIR = "$FIGURE_OUTPUT_DIR"
TABLE_OUTPUT_DIR = "$TABLE_OUTPUT_DIR"

CONFIDENCE = 0.2
IMAGE_SIZE = 1024

HORIZONTAL_PADDING = 60
VERTICAL_PADDING = 10

# ----------------------------------------
# SETUP
# ----------------------------------------

os.makedirs(FIGURE_OUTPUT_DIR, exist_ok=True)
os.makedirs(TABLE_OUTPUT_DIR, exist_ok=True)

print("Loading model...")

model = YOLOv10(MODEL_PATH)

pages = sorted(glob.glob(PAGE_PATTERN))

print(f"Found {len(pages)} pages")

figure_metadata = []
table_metadata = []

# ----------------------------------------
# HELPERS
# ----------------------------------------

def area(box):
    x1, y1, x2, y2 = box
    return (x2 - x1) * (y2 - y1)

def inside(boxA, boxB):
    ax1, ay1, ax2, ay2 = boxA
    bx1, by1, bx2, by2 = boxB

    return (
        ax1 >= bx1 and
        ay1 >= by1 and
        ax2 <= bx2 and
        ay2 <= by2
    )

def clean_ocr_text(text):
    # ----------------------------------------
    # REMOVE LINE BREAKS
    # ----------------------------------------

    text = text.replace("\n", " ")

    # ----------------------------------------
    # FIX HYPHENATED LINE WRAPS
    # ----------------------------------------

    # attention-\nbased -> attentionbased

    text = re.sub(
        r'-\s+',
        '',
        text
    )

    # ----------------------------------------
    # COLLAPSE WHITESPACE
    # ----------------------------------------

    text = re.sub(
        r'\s+',
        ' ',
        text
    )


    cleaned = text.replace("|", "1")
    cleaned = cleaned.replace("I", "1")
    cleaned = cleaned.replace("l", "1")

    return cleaned.strip()

def extract_caption(orig, cap_box):

    cx1, cy1, cx2, cy2 = cap_box

    caption_crop = orig[cy1:cy2, cx1:cx2]

    gray = cv2.cvtColor(
        caption_crop,
        cv2.COLOR_BGR2GRAY
    )

    _, thresh = cv2.threshold(
        gray,
        180,
        255,
        cv2.THRESH_BINARY
    )

    text = pytesseract.image_to_string(thresh)

    return clean_ocr_text(text)

def filter_nested_boxes(boxes):

    filtered = []

    for box in boxes:

        keep = True

        for other in boxes:

            if box == other:
                continue

            if inside(box, other):

                if area(box) < area(other):
                    keep = False
                    break

        if keep:
            filtered.append(box)

    return filtered

def roman_to_int(s):

    roman = {
        'I': 1,
        'V': 5,
        'X': 10,
        'L': 50,
        'C': 100,
        'D': 500,
        'M': 1000
    }

    total = 0
    prev = 0

    for ch in reversed(s.upper()):

        value = roman[ch]

        if value < prev:
            total -= value
        else:
            total += value

        prev = value

    return total

def save_crop(
    orig,
    box,
    output_dir,
    filename
):

    x1, y1, x2, y2 = box

    px1 = max(0, x1 - HORIZONTAL_PADDING)
    py1 = max(0, y1 - VERTICAL_PADDING)

    px2 = min(orig.shape[1], x2 + HORIZONTAL_PADDING)
    py2 = min(orig.shape[0], y2 + VERTICAL_PADDING)

    crop = orig[py1:py2, px1:px2]

    if crop.size == 0:
        return None, None, None

    output_path = os.path.join(
        output_dir,
        filename
    )

    cv2.imwrite(output_path, crop)

    return output_path, crop.shape[1], crop.shape[0]

# ----------------------------------------
# PROCESS PAGES
# ----------------------------------------

for page_path in pages:

    print(f"\\nProcessing {page_path}")

    results = model.predict(
        page_path,
        imgsz=IMAGE_SIZE,
        conf=CONFIDENCE
    )

    orig = cv2.imread(page_path)

    if orig is None:
        print(f"Could not read {page_path}")
        continue

    figures = []
    figure_captions = []

    tables = []
    table_captions = []

    # ----------------------------------------
    # COLLECT DETECTIONS
    # ----------------------------------------

    for r in results:

        boxes = r.boxes.xyxy.cpu().numpy()
        classes = r.boxes.cls.cpu().numpy()

        for box, cls_id in zip(boxes, classes):

            label = r.names[int(cls_id)]

            box = tuple(map(int, box))

            if label == "figure":
                figures.append(box)

            elif label == "figure_caption":
                figure_captions.append(box)

            elif label == "table":
                tables.append(box)

            elif label == "table_caption":
                table_captions.append(box)

    print(f"Detected {len(figures)} figures")
    print(f"Detected {len(tables)} tables")

    # ----------------------------------------
    # FILTER DUPLICATES
    # ----------------------------------------

    figures = filter_nested_boxes(figures)
    tables = filter_nested_boxes(tables)

    # ----------------------------------------
    # PROCESS FIGURES
    # ----------------------------------------

    for fig in figures:

        fx1, fy1, fx2, fy2 = fig

        best_caption = None
        best_distance = 999999

        for cap in figure_captions:

            cx1, cy1, cx2, cy2 = cap

            if cy1 > fy2:

                distance = cy1 - fy2

                if distance < best_distance:
                    best_distance = distance
                    best_caption = cap

        if best_caption is None:
            continue

        caption = extract_caption(
            orig,
            best_caption
        )

        print("Figure caption:", caption)

        match = re.search(
            r'(?:Figure|Fig\.?)\s*[:.]?\s*(\d+)',
            caption,
            re.IGNORECASE
        )

        if not match:
            print("Could not extract figure number")
            continue

        figure_number = match.group(1)

        filename = f"figure_{figure_number}.png"

        output_path, width, height = save_crop(
            orig,
            fig,
            FIGURE_OUTPUT_DIR,
            filename
        )

        if output_path is None:
            continue

        print(f"Saved {output_path}")

        figure_metadata.append({
            "figure_id": int(figure_number),
            "image_path": output_path,
            "caption": caption,
            "width": int(width),
            "height": int(height)
        })

    # ----------------------------------------
    # PROCESS TABLES
    # ----------------------------------------

    for tbl in tables:

        tx1, ty1, tx2, ty2 = tbl

        best_caption = None
        best_distance = 999999

        for cap in table_captions:

            cx1, cy1, cx2, cy2 = cap

            distance = min(
                abs(cy2 - ty1),
                abs(cy1 - ty2)
            )

            if distance < best_distance:
                best_distance = distance
                best_caption = cap

        if best_caption is None:
            continue

        caption = extract_caption(
            orig,
            best_caption
        )

        normalized_caption = caption

        # common OCR mistakes
        normalized_caption = normalized_caption.replace(
            "Tab1e",
            "Table"
        )

        normalized_caption = normalized_caption.replace(
            "TAB1E",
            "TABLE"
        )

        print("Table caption:", normalized_caption)

        match = re.search(
            r'(?:TABLE|Table)\s*([IVXLCDM]+|[0-9]+)',
            normalized_caption,
            re.IGNORECASE
        )

        if not match:
            print("Could not extract table number")
            continue

        table_number_raw = match.group(1)

        # ----------------------------------------
        # OCR FIXES FOR ROMAN NUMERALS
        # ----------------------------------------

        # OCR often converts:
        # III -> 111
        # II  -> 11
        # IV  -> 1V

        if re.fullmatch(r'[0-9]+', table_number_raw):

            # if only composed of 1s,
            # interpret as Roman numeral I repetitions

            if set(table_number_raw) == {"1"}:

                roman_candidate = (
                    table_number_raw
                    .replace("1", "I")
                )

                table_number = roman_to_int(
                    roman_candidate
                )

            else:
                table_number = int(table_number_raw)

        else:

            roman_candidate = (
                table_number_raw
                .replace("1", "I")
            )

            table_number = roman_to_int(
                roman_candidate
            )

        filename = f"table_{table_number}.png"

        output_path, width, height = save_crop(
            orig,
            tbl,
            TABLE_OUTPUT_DIR,
            filename
        )

        if output_path is None:
            continue

        print(f"Saved {output_path}")
        
        # replace OCR table identifier with normalized one
        caption = re.sub(
            r'(TABLE|Table)\s+([IVXLCDM]+|[0-9]+)',
            f'Table {table_number}',
            caption,
            flags=re.IGNORECASE
        )

        table_metadata.append({
            "table_id": int(table_number),
            "image_path": output_path,
            "caption": caption,
            "width": int(width),
            "height": int(height)
        })

# ----------------------------------------
# WRITE FIGURE METADATA
# ----------------------------------------

figure_metadata_path = os.path.join(
    FIGURE_OUTPUT_DIR,
    "metadata.json"
)

with open(
    figure_metadata_path,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        figure_metadata,
        f,
        indent=2,
        ensure_ascii=False
    )

# ----------------------------------------
# WRITE TABLE METADATA
# ----------------------------------------

table_metadata_path = os.path.join(
    TABLE_OUTPUT_DIR,
    "metadata.json"
)

with open(
    table_metadata_path,
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        table_metadata,
        f,
        indent=2,
        ensure_ascii=False
    )

print(f"Saved figure metadata: {figure_metadata_path}")
print(f"Saved table metadata: {table_metadata_path}")

print("\\nDone.")

EOF

echo ""
echo "All figures saved to ./$FIGURE_OUTPUT_DIR/"
echo "All tables saved to ./$TABLE_OUTPUT_DIR/"
echo "Temporary files removed."