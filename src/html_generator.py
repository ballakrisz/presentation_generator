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
- max 2 major visuals per slide
- max 2 tables per slide

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
- row layouts
- side-by-side layouts
- SEE BELOW FOR THE ALLOWED LAYOUT TYPES

** PRIORITIZE visual/table content readability when choosing layouts **

A slide should communicate ONE coherent idea.

DO NOT create:
- isolated image-only slides

unless absolutely necessary.

Text-only slides ARE allowed when:
- no meaningful visual exists
- the content is conceptual
- the content is summary-oriented
- the content is discussion-oriented

** IMPORTANT **
- ITS COMPLETELY FINE IF A SLIDE HAS NO MATCHING VISUAL
- IN THIS CASE USE A TEXT-ONLY SLIDE, RATHER THAN INSERTING SOME UNRELATED FIGURES.

==================================================
VISUAL USAGE RULES
==================================================

Use visuals ONLY when semantically relevant.

DO NOT SQUEEZE LARGE VISUALS, MAINTAIN READABILITY 

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

A FIGURE'S CAPTION SHOULD BE THE SAME AS IN THE SOURCE DOCUMENT IF POSSIBLE.

==================================================
TABLE RULES
==================================================

Tables MUST be semantically relevant.

DO NOT reuse tables multiple times.

ALL TABLES ON A SLIDE SHOULD BE ACCOMPANIED BY
2-3 BULLET POINTS EXPLAINING THE MAJOR FINDING.

COMPACT TABLE LAYOUT RULES:

If a table is narrow or contains only a few rows/columns:
- MUST use table-layout
- place bullet points on the left
- place the table on the right

Large tables SHOULD use:
- text above
- table below
- stacked layouts

==================================================
REFERENCES RULES
==================================================

Include references ONLY if:
- prior work is explicitly discussed
- external methods/frameworks are mentioned
- citations appear in slide text

DO NOT generate a references slide automatically.

==================================================
ADAPTIVE LAYOUT RULES
==================================================

LAYOUT SELECTION MUST PRIORITIZE BOTH:
- figure readability
- and aspect ratio efficiency.

IMPORTANT:
Choose layouts using BOTH:
1. visual density
2. figure aspect ratio

==================================================
ROW LAYOUT (image right, bullets left)
==================================================

USE ROW LAYOUT FOR:
- dense technical diagrams
- transformer/network diagrams
- architecture figures with many components
- figures with many labels
- figures with small embedded text
- complex multi-component visualizations

These figures require LARGE DISPLAY SIZE
to remain readable.

IMPORTANT:
If shrinking the figure vertically would make:
- labels unreadable
- text tiny
- structure unclear

THEN USE ROW LAYOUT.

==================================================
STACKED LAYOUT (bullets top, image bottom)
==================================================

USE STACKED LAYOUT FOR:
- wide panoramic figures
- horizontal workflows
- pipelines
- process overviews
- simple charts
- bar plots
- line plots
- visually simple wide diagrams

IMPORTANT:
Wide figures SHOULD use stacked layout
WHEN:
- the figure remains readable at reduced height
- labels remain readable
- the diagram is not visually dense

==================================================
LAYOUT DECISION RULE
==================================================

FIRST determine:
- is the figure visually dense?

If YES:
- use row layout

If NO:
- evaluate aspect ratio

If the figure is:
- wide
- horizontal
- panoramic

THEN:
- use stacked layout

IMPORTANT:
Simple wide workflows/pipelines SHOULD usually
use stacked layout.

Dense technical figures SHOULD usually
use row layout.

Readability is ALWAYS more important
than maximizing image size.

TEXT-ONLY SLIDES MUST:
- use text-layout
- use the FULL slide width
- NEVER reserve empty space for visuals
- NEVER behave like a row layout

==================================================
STRICT HTML STRUCTURE RULES
==================================================

You MUST use EXACTLY the following structures.

ALLOWED HTML ELEMENTS ONLY:
- html
- head
- body
- section
- div
- ul
- li
- img
- table
- thead
- tbody
- tr
- th
- td

DO NOT USE:
- p
- span
- article
- aside
- h1-h6
- figure
- figcaption
- inline styles
- arbitrary wrappers
- custom class names

==================================================
TITLE SLIDE
==================================================

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

==================================================
ROW LAYOUT SLIDE
==================================================

<section class="slide">

    <div class="slide-title">
        SLIDE TITLE
    </div>

    <div class="slide-content row-layout">

        <div class="content-column">

            <ul>
                <li>Bullet point</li>
            </ul>

        </div>

        <div class="visual-container">

            <div class="figure-wrapper">

                <img src="IMAGE_PATH">

                <div class="caption">
                    Figure caption
                </div>

            </div>

        </div>

    </div>

</section>

==================================================
STACKED LAYOUT SLIDE
==================================================

<section class="slide">

    <div class="slide-title">
        SLIDE TITLE
    </div>

    <div class="slide-content column-layout">

        <div class="content-column">

            <ul>
                <li>Bullet point</li>
            </ul>

        </div>

        <div class="visual-container">

            <div class="figure-wrapper">

                <img src="IMAGE_PATH">

                <div class="caption">
                    Figure caption
                </div>

            </div>

        </div>

    </div>

</section>

==================================================
TEXT-ONLY SLIDE
==================================================

<section class="slide">

    <div class="slide-title">
        SLIDE TITLE
    </div>

    <div class="slide-content text-layout">

        <div class="content-column">

            <ul>
                <li>Bullet point</li>
            </ul>

        </div>

    </div>

</section>

==================================================
COMPACT TABLE LAYOUT
==================================================

Use this layout for:
- small tables
- narrow tables

<section class="slide">

    <div class="slide-title">
        SLIDE TITLE
    </div>

    <div class="slide-content table-layout">

        <div class="content-column">

            <ul>
                <li>Important finding</li>
                <li>Another observation</li>
            </ul>

        </div>

        <div class="visual-container">

            <div class="table-container">

                <table>
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr>
                            <td>F1</td>
                            <td>0.82</td>
                        </tr>
                    </tbody>

                </table>

            </div>

        </div>

    </div>

</section>

==================================================
TABLE STRUCTURE
==================================================

<div class="table-container">

    <table>
        <thead>
            <tr>
                <th>Header</th>
            </tr>
        </thead>

        <tbody>
            <tr>
                <td>Value</td>
            </tr>
        </tbody>
    </table>

</div>

==================================================
REFERENCE STRUCTURE
==================================================

<ul class="references">
    <li>Reference item</li>
</ul>

==================================================
IMPORTANT FIGURE RULES
==================================================

- EVERY figure MUST include a caption with figure numbering
- captions MUST appear BELOW the image
- captions MUST use class="caption"
- images MUST use standard img tags
- DO NOT omit captions
- DO NOT place captions outside figure-wrapper

==================================================
HTML REQUIREMENTS
==================================================

RETURN ONLY VALID HTML.

DO NOT include:
- CSS
- JavaScript
- markdown
- code fences

Generate semantic HTML ONLY.

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

    .slide-content.text-layout {
        display: flex;

        flex-direction: column;

        justify-content: center;

        align-items: stretch;

        height: 100%;
    }

    .slide-content.text-layout .content-column {
        flex: 1;

        display: flex;

        flex-direction: column;

        justify-content: center;
    }

    .slide-content.text-layout ul {
        display: flex;

        flex-direction: column;

        justify-content: center;

        gap: 22px;

        width: 100%;
    }

    .slide-content.text-layout li {
        margin-bottom: 0;

        font-size: 32px;

        line-height: 1.4;
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

        justify-content: center;
    }

    .slide-content.row-layout li {
        font-size: 28px;
        line-height: 1.4;
    }

    .slide-content.row-layout .visual-container {
        flex: 1;
    }

    .slide-content.table-layout {
        flex-direction: row;

        align-items: center;
    }

    .slide-content.table-layout li {
        font-size: 30px;
        line-height: 1.4;
    }

    .slide-content.table-layout .content-column {
        flex: 0 0 52%;

        justify-content: center;
    }

    .slide-content.table-layout .visual-container {
        flex: 1;

        align-items: center;
    }

    .content-column {
        flex: 1;

        min-width: 0;

        display: flex;
        flex-direction: column;

        justify-content: flex-start;
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

        margin-bottom: 12px;
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

        margin-top: 18px;
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