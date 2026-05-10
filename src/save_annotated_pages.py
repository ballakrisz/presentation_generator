from doclayout_yolo import YOLOv10
import cv2
import glob
import os

# ----------------------------------------
# CONFIG
# ----------------------------------------

MODEL_PATH = "doclayout_yolo_docstructbench_imgsz1024.pt"
PAGE_PATTERN = "page-14.png"
OUTPUT_DIR = "annotated_pages"

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

for page_path in pages:

    print(f"Processing {page_path}")

    # run detection
    results = model.predict(
        page_path,
        imgsz=IMAGE_SIZE,
        conf=CONFIDENCE
    )

    # original image
    image = cv2.imread(page_path)

    if image is None:
        print(f"Could not read {page_path}")
        continue

    # draw detections
    for r in results:

        boxes = r.boxes.xyxy.cpu().numpy()
        classes = r.boxes.cls.cpu().numpy()

        for box, cls_id in zip(boxes, classes):

            label = r.names[int(cls_id)]

            x1, y1, x2, y2 = map(int, box)

            # draw rectangle
            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                (255, 0, 0),
                4
            )

            # draw label
            cv2.putText(
                image,
                label,
                (x1, max(20, y1 - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 0, 0),
                3
            )

    # save annotated page
    output_path = os.path.join(
        OUTPUT_DIR,
        os.path.basename(page_path)
    )

    cv2.imwrite(output_path, image)

    print(f"Saved {output_path}")

print("\nDone.")