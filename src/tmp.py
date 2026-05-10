from doclayout_yolo import YOLOv10
import cv2
import glob
import os

# ----------------------------------------
# CONFIG
# ----------------------------------------

MODEL_PATH = "doclayout_yolo_docstructbench_imgsz1024.pt"
PAGE_PATTERN = "page-*.png"
OUTPUT_DIR = "figures"

CONFIDENCE = 0.2
IMAGE_SIZE = 1024

# ----------------------------------------
# CREATE OUTPUT DIRECTORY
# ----------------------------------------

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ----------------------------------------
# LOAD MODEL
# ----------------------------------------

print("Loading model...")

model = YOLOv10(MODEL_PATH)

# ----------------------------------------
# FIND PAGE IMAGES
# ----------------------------------------

pages = sorted(glob.glob(PAGE_PATTERN))

print(f"Found {len(pages)} pages")

# ----------------------------------------
# PROCESS PAGES
# ----------------------------------------

figure_counter = 1

for page_path in pages:

    print(f"\nProcessing {page_path}")

    # run detection
    results = model.predict(
        page_path,
        imgsz=IMAGE_SIZE,
        conf=CONFIDENCE
    )

    # load original image
    orig = cv2.imread(page_path)

    if orig is None:
        print(f"Could not read {page_path}")
        continue

    # iterate detections
    for r in results:

        boxes = r.boxes.xyxy.cpu().numpy()
        classes = r.boxes.cls.cpu().numpy()

        for box, cls_id in zip(boxes, classes):

            label = r.names[int(cls_id)]

            # only keep figures
            if label != "figure":
                continue

            x1, y1, x2, y2 = map(int, box)

            # safety clamp
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(orig.shape[1], x2)
            y2 = min(orig.shape[0], y2)

            # crop figure
            crop = orig[y1:y2, x1:x2]

            # skip empty crops
            if crop.size == 0:
                print("Skipped empty crop")
                continue

            # output filename
            output_path = os.path.join(
                OUTPUT_DIR,
                f"figure_{figure_counter}.png"
            )

            # save
            cv2.imwrite(output_path, crop)

            print(f"Saved {output_path}")

            figure_counter += 1

print("\nDone.")
print(f"Saved {figure_counter - 1} figures.")