import os
import fitz
import re


def extract_images_with_context(
    pdf_path,
    output_folder
):
    os.makedirs(output_folder, exist_ok=True)

    pdf = fitz.open(pdf_path)

    indexed_images = []

    figure_counter = 1

    figure_pattern = re.compile(
        r"(Fig(?:ure)?\.?\s*\d+.*?)$",
        re.IGNORECASE
    )

    for page_number in range(len(pdf)):
        page = pdf[page_number]

        page_text = page.get_text()

        lines = page_text.splitlines()

        images = page.get_images(full=True)

        for image_index, img in enumerate(images):
            try:
                xref = img[0]

                base_image = pdf.extract_image(xref)

                image_bytes = base_image["image"]

                image_ext = base_image["ext"]

                image_filename = (
                    f"figure_{figure_counter}.{image_ext}"
                )

                image_path = os.path.join(
                    output_folder,
                    image_filename
                )

                with open(image_path, "wb") as f:
                    f.write(image_bytes)


                indexed_images.append({
                    "figure_id": figure_counter,
                    "image_path": image_path,
                    "page": page_number + 1,
                    "context": page_text[:500]
                })

                figure_counter += 1
                

            except Exception as e:
                print("Image extraction failed:", e)

    return indexed_images