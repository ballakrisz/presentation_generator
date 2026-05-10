import argparse
import subprocess
import json
from pathlib import Path

from document_reader import (
    extract_document_text
)

from html_generator import (
    generate_html_presentation
)

from pdf_exporter import (
    export_html_to_pdf
)


BASE_DIR = Path(__file__).resolve().parent


def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Generate an AI-designed presentation "
            "from a PDF document."
        )
    )

    parser.add_argument(
        "--input",
        type=str,
        required=True,
        help=(
            "Relative path to input PDF "
            "(relative to main.py)"
        )
    )

    parser.add_argument(
        "--html-output",
        type=str,
        default="output/presentation.html",
        help=(
            "Relative path to generated HTML output "
            "(relative to main.py)"
        )
    )

    parser.add_argument(
        "--pdf-output",
        type=str,
        default=(
            "output/generated_presentation.pdf"
        ),
        help=(
            "Relative path to generated PDF output "
            "(relative to main.py)"
        )
    )

    parser.add_argument(
        "--temp-image-folder",
        type=str,
        default="temp_images",
        help=(
            "Relative temp directory for extracted "
            "figures/images"
        )
    )

    parser.add_argument(
        "--temp-table-folder",
        type=str,
        default="temp_tables",
        help=(
            "Relative temp directory for extracted "
            "tables"
        )
    )

    return parser.parse_args()


def resolve_relative_path(path_str):
    return (
        BASE_DIR / path_str
    ).resolve()


def main():
    args = parse_args()

    input_pdf = resolve_relative_path(
        args.input
    )

    output_html = resolve_relative_path(
        args.html_output
    )

    output_pdf = resolve_relative_path(
        args.pdf_output
    )

    input_stem = input_pdf.stem

    output_html.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    output_pdf.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print("Extracting document text...")

    document_text = extract_document_text(
        str(input_pdf)
    )

    print("Extracting figures and tables...")

    subprocess.run(
        [
            str(BASE_DIR / "extract_figures.sh"),
            "--input",
            str(input_pdf)
        ],
        check=True
    )

    # ----------------------------------------
    # FIGURES
    # ----------------------------------------

    figure_dir = (
        BASE_DIR /
        "figures" /
        input_stem
    )

    figure_metadata_path = (
        figure_dir /
        "metadata.json"
    )

    if not figure_metadata_path.exists():
        raise FileNotFoundError(
            f"Figure metadata missing: "
            f"{figure_metadata_path}"
        )

    with open(
        figure_metadata_path,
        "r",
        encoding="utf-8"
    ) as f:
        indexed_images = json.load(f)

    # ----------------------------------------
    # TABLES
    # ----------------------------------------

    table_dir = (
        BASE_DIR /
        "tables" /
        input_stem
    )

    table_metadata_path = (
        table_dir /
        "metadata.json"
    )

    if not table_metadata_path.exists():
        raise FileNotFoundError(
            f"Table metadata missing: "
            f"{table_metadata_path}"
        )

    with open(
        table_metadata_path,
        "r",
        encoding="utf-8"
    ) as f:
        indexed_tables = json.load(f)

    print(
        f"Loaded {len(indexed_images)} figures"
    )

    print(
        f"Loaded {len(indexed_tables)} tables"
    )

    print(
        "Generating presentation..."
    )

    generate_html_presentation(
        document_text,
        indexed_images,
        indexed_tables,
        str(output_html)
    )

    print("Exporting PDF...")

    export_html_to_pdf(
        str(output_html),
        str(output_pdf)
    )

    print("DONE!")


if __name__ == "__main__":
    main()