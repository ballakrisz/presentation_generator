from pathlib import Path

from playwright.sync_api import (
    sync_playwright
)


def export_html_to_pdf(
    html_path,
    output_pdf
):
    absolute_html_path = (
        Path(html_path)
        .resolve()
        .as_uri()
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        page = browser.new_page()

        page.goto(
            absolute_html_path,
            wait_until="networkidle"
        )

        page.pdf(
            path=output_pdf,
            print_background=True,
            prefer_css_page_size=True
        )

        browser.close()