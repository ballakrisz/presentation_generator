import json
import os
import re

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def generate_html_presentation(
    document_text,
    indexed_images,
    output_html
):
    figures_description = []

    for image in indexed_images:
        absolute_path = os.path.abspath(
            image["image_path"]
        )

        figures_description.append({
            "figure_id": image["figure_id"],
            "image_path": absolute_path,
            "caption": image.get(
                "caption",
                ""
            ),
            "width": image.get("width"),
            "height": image.get("height"),
            "ocr_text": image.get("ocr_text", ""),
            "section": image.get("section", "")
        })

    figures_json = json.dumps(
        figures_description,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are an expert presentation designer specialized in converting arbitrary documents into professional presentation slides.

Generate a COMPLETE printable HTML presentation.

The input document may belong to ANY domain.

Adapt automatically to the actual content.

==================================================
PRIMARY OBJECTIVE
==================================================

Transform the source document into a visually clear,
presentation-oriented slide deck.

This is a PRESENTATION.
NOT a report.

==================================================
GENERAL CONTENT RULES
==================================================

- Use ONLY provided visuals/tables
- Preserve original meaning
- Prefer concise presentation language
- Avoid long paragraphs
- Avoid walls of text
- Avoid duplicate content
- Avoid repeating the same idea across slides

IMPORTANT:
Do NOT force every section into a slide.

Prioritize:
- key findings
- major concepts
- workflows
- comparisons
- results
- conclusions
- important visuals

==================================================
TITLE SLIDE RULES
==================================================

The FIRST slide is a dedicated title slide.

The title slide MUST contain ONLY:
- document/paper title
- authors
- affiliations

DO NOT include:
- bullet points
- summaries
- objectives
- abstracts
- keywords
- visuals
- references

TITLE SLIDE LAYOUT:

- title centered vertically and horizontally
- very large title
- authors below title
- affiliations below authors
- clean minimal appearance

==================================================
SLIDE STRUCTURE RULES
==================================================

EVERY slide MUST:
- fit fully inside 1280x720
- contain readable content
- avoid overflow
- avoid overlap
- remain visually balanced

STRICT LIMITS:
- max 6 bullets per slide
- max 20 words per bullet
- max 80 total words per slide
- max 2 major visual per slide
- max 2 table per slide

If content exceeds limits:
- summarize
- simplify

==================================================
CONTENT COHESION RULES
==================================================

IMPORTANT:
Related bullets and their corresponding visuals
MUST remain on the SAME slide whenever possible.

DO NOT split:
- explanations and their figure
- metrics and their chart
- workflow bullets and workflow diagram
- model description and architecture figure
- results bullets and result visualization

UNLESS:
- readability would be severely harmed
- content physically cannot fit

Prefer:
- mixed layouts
- side-by-side layouts

OVER splitting related content across slides.

A slide should communicate ONE coherent idea.

DO NOT create:
- isolated image-only slides
- isolated bullet-only slides

unless absolutely necessary.

==================================================
VISUAL USAGE RULES
==================================================

Use visuals ONLY when semantically relevant.

CRITICAL:
Visuals MUST match slide topic.

Use:
- captions
- OCR text
- nearby document context
- titles
- terminology

to determine relevance.

DO NOT randomly assign visuals.

==================================================
FIGURE MATCHING RULES
==================================================

Determine semantic role of figures dynamically.

Use figures ONLY on semantically matching slides.

IMPORTANT:
A figure should support the slide message.

LOOK FOR THE CAPTION OF A FIGURE TO INFER ITS MEANING (IF A CAPTION SAYS FIGURE 1, THEN THE CORRESPONDING IMAGE IS "figure_1.png")

ALWAYS INCLUDE A FIGURE'S CAPTION UNDER IT

==================================================
SEMANTIC FIGURE DISAMBIGUATION
==================================================

IMPORTANT:
Different evaluation figures may appear visually similar.

You MUST use:
- captions
- OCR text
- axis labels
- legends
- keywords
- surrounding document context

to determine the correct slide placement.

==================================================
TABLE RULES
==================================================

Tables MUST be semantically relevant.

DO NOT reuse tables multiple times.

LOOK FOR TABLES IN THE DOCUMENT, AND INFER THE CORRECT PLACEMENT OF THEM ON THE SLIDES

ALL TABLES ON A SLIDE SHOULD BE ACCOMPANIED BY 2-3 BULLETPOINTS EXPLAINING THE MAYOR FINDING/MESSAGE OF THE TABLE

==================================================
REFERENCES RULES
==================================================

Include references ONLY if:
- prior work is explicitly discussed
- external methods/frameworks are mentioned
- citations appear in slide text

DO NOT generate a references slide automatically.

If references are included:
- every reference MUST be cited somewhere
- include ONLY referenced items

==================================================
LAYOUT GUIDELINES
==================================================

Prefer:
- mixed layouts
- side-by-side layouts
- balanced text + figure layouts

DO NOT aggressively separate:
- figures from explanations
- charts from metrics
- workflows from descriptions

==================================================
ADAPTIVE LAYOUT RULES
==================================================

The layout MUST adapt to the aspect ratio
of the selected visual.

FOR WIDE FIGURES:
- use stacked layout
- figure on top
- bullets below
- avoid narrow bullet columns

Wide figures include:
- pipelines
- workflow diagrams
- horizontal charts
- panoramic visualizations
- wide architecture diagrams

FOR TALL OR SQUARE FIGURES:
- use side-by-side layout
- bullets on left
- figure on right

IMPORTANT:
Never compress bullet text into narrow columns.

If bullet lines wrap excessively:
- switch to stacked layout

Readability is more important than
maintaining a fixed layout style.

==================================================
VISUAL SCALING RULES
==================================================

Maintain readability of visuals.

IMPORTANT:
Visuals containing:
- text
- labels
- diagrams
- metrics
- legends
- annotations

must remain readable.

DO NOT:
- aggressively shrink visuals
- crop important regions
- distort aspect ratios

==================================================
STRICT HTML STRUCTURE RULES
==================================================

You MUST use EXACTLY the following HTML structure.

TITLE SLIDE:

<section class="slide title-slide">

    <div class="slide-title">
        TITLE HERE
    </div>

    <div class="authors">
        AUTHORS HERE
    </div>

    <div class="affiliations">
        AFFILIATIONS HERE
    </div>

</section>

NORMAL SLIDE:

<section class="slide">

    <div class="slide-title">
        SLIDE TITLE
    </div>

    <div class="slide-content row-layout">

        <div class="content-column">
            CONTENT HERE
        </div>

        <div class="visual-container">
            VISUAL HERE
        </div>

    </div>

</section>

STACKED LAYOUT:

<section class="slide">

    <div class="slide-title">
        SLIDE TITLE
    </div>

    <div class="slide-content column-layout">

        <div class="visual-container">
            VISUAL HERE
        </div>

        <div class="content-column">
            CONTENT HERE
        </div>

    </div>

</section>

TEXT-ONLY SLIDE:

<section class="slide">

    <div class="slide-title">
        SLIDE TITLE
    </div>

    <div class="slide-content text-layout">

        <div class="content-column">
            CONTENT HERE
        </div>

    </div>

</section>

FIGURE STRUCTURE:

<div class="visual-container">

    <div class="figure-wrapper">

        <img src="IMAGE_PATH">

        <div class="caption">
            FIGURE CAPTION
        </div>

    </div>

</div>

IMPORTANT:
- EVERY figure MUST include its caption with the FIGURE NUMBER
- captions MUST appear BELOW the image
- captions MUST use class="caption"
- images MUST use standard <img> tags
- DO NOT place captions outside figure-wrapper
- DO NOT omit captions

IMPORTANT:
DO NOT:
- invent new layout class names
- invent new title structures
- use h1/h2 tags
- use inline styles
- use nested wrappers unnecessarily

Use ONLY the provided class names.

==================================================
STYLE RULES
==================================================

Use:
- modern conference presentation aesthetics
- dark professional theme
- strong visual hierarchy
- readable typography
- balanced whitespace
- clean spacing
- flexbox layouts

Slides should feel:
- modern
- polished
- presentation-oriented
- visually coherent

==================================================
HTML REQUIREMENTS
==================================================

RETURN ONLY VALID HTML.

The HTML MUST:
- contain inline CSS
- contain all slides
- contain no JavaScript
- contain no external dependencies

EVERY slide MUST use:

<section class="slide">

EVERY slide MUST contain:

<div class="slide-title">

==================================================
CSS REQUIREMENTS
==================================================

Images MUST follow:

img {{
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}}

==================================================
FIGURES
==================================================

{figures_json}

==================================================
DOCUMENT
==================================================

{document_text}
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        temperature=0.25,
        messages=[
            {
                "role": "system",
                "content": (
                    "You generate professional "
                    "conference presentation HTML."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    html = response.choices[0].message.content

    html = html.replace(
        "```html",
        ""
    )

    html = html.replace(
        "```",
        ""
    )

    html = re.sub(
        r"<style.*?>.*?</style>",
        "",
        html,
        flags=re.DOTALL
    )

    html = re.sub(
        r"<script.*?>.*?</script>",
        "",
        html,
        flags=re.DOTALL
    )

    css = """
    <style>

    @page {
        size: 1280px 720px;
        margin: 0;
    }

    html, body {
        margin: 0;
        padding: 0;
        background: #111827;
        font-family: Arial, sans-serif;
    }

    body {
        margin: 0;
        padding: 0;
    }

    .slide {
        width: 1280px;
        height: 720px;

        box-sizing: border-box;

        padding: 42px;

        page-break-after: always;
        break-after: page;

        background: linear-gradient(
            135deg,
            #111827,
            #1f2937
        );

        color: white;

        overflow: hidden;

        display: flex;
        flex-direction: column;

        position: relative;
    }

    .slide-title {
        font-size: 38px;
        font-weight: 700;

        margin-bottom: 24px;

        color: white;

        flex-shrink: 0;
    }

    .slide-content {
        flex: 1;

        display: flex;

        gap: 36px;

        overflow: hidden;

        min-height: 0;

        align-items: stretch;
    }

    .slide-content.row-layout {
        flex-direction: row;
    }

    .slide-content.column-layout {
        flex-direction: column;
    }

    .slide-content.column-layout .visual-container {
        flex: 0 0 58%;
    }

    .slide-content.column-layout .content-column {
        flex: 1;
    }

    .slide-content.column-layout li {
        font-size: 26px;
        line-height: 1.35;
    }

    .slide-content.row-layout .content-column {
        max-width: 34%;
    }

    .slide-content.row-layout .visual-container {
        flex: 1;
    }

    .content-column {
        flex: 1;

        min-width: 0;

        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .visual-container {
        flex: 1;

        min-height: 0;
        min-width: 0;

        display: flex;

        align-items: center;
        justify-content: center;

        overflow: hidden;
    }

    img {
        max-width: 100%;
        max-height: 100%;

        object-fit: contain;

        border-radius: 14px;

        box-shadow:
            0 10px 30px rgba(0,0,0,0.35);
    }

    ul {
        margin: 0;
        padding-left: 28px;
    }

    li {
        font-size: 24px;
        line-height: 1.4;

        margin-bottom: 14px;
    }

    .figure-wrapper {
        width: 100%;
        height: 100%;

        display: flex;
        flex-direction: column;

        align-items: center;
        justify-content: center;

        overflow: hidden;
    }

    .figure-wrapper img {
        flex: 1;

        min-height: 0;
    }

    .caption {
        width: 100%;

        margin-top: 14px;

        font-size: 15px;

        line-height: 1.35;

        color: #cbd5e1;

        text-align: center;

        opacity: 0.92;
    }

    .title-slide {
        width: 1280px;
        height: 720px;

        box-sizing: border-box;

        display: flex;
        flex-direction: column;

        justify-content: center;
        align-items: center;

        text-align: center;

        padding: 80px 120px;

        overflow: hidden;
    }

    .title-slide .slide-title {
        all: unset;

        display: block;

        width: 100%;

        font-family: Arial, sans-serif;

        font-size: 50px;

        line-height: 1.08;

        font-weight: 900;

        color: white;

        text-align: center;

        letter-spacing: -2px;

        margin-bottom: 54px;
    }

    .title-slide .authors {
        width: 100%;

        font-size: 38px;

        line-height: 1.35;

        font-weight: 500;

        color: #d1d5db;

        text-align: center;

        margin-bottom: 30px;
    }

    .title-slide .affiliations {
        width: 100%;

        font-size: 26px;

        line-height: 1.45;

        font-weight: 400;

        color: #9ca3af;

        text-align: center;

        opacity: 0.95;
    }

    table {
        width: 100%;

        border-collapse: collapse;

        overflow: hidden;

        border-radius: 12px;

        background: white;

        color: black;

        font-size: 18px;

        margin-bottom: 34px;
    }

    th {
        background: #2563eb;

        color: white;

        padding: 12px;

        text-align: left;
    }

    td {
        padding: 10px;

        border: 1px solid #d1d5db;
    }

    .table-container {
        width: 100%;

        overflow: hidden;
    }

    .references {
        font-size: 16px;

        line-height: 1.4;

        overflow: hidden;
    }

    .references li {
        font-size: 16px;

        margin-bottom: 8px;
    }

    </style>
    """

    if "<head>" in html:
        html = html.replace(
            "<head>",
            f"<head>{css}"
        )
    else:
        html = f"<head>{css}</head>{html}"

    with open(
        output_html,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(html)