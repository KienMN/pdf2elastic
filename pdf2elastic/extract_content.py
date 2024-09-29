import logging
import os
from typing import Any, Generator

import extract_index
import pdfplumber
from pdf_components import Heading, Paragraph

logger = logging.getLogger(__name__)

LINE_SPACE = 20
HEADER = "Amazon Simple Storage Service User Guide"
FOOTER = "API Version 2006-03-01"
HEADER_FONT_SIZE = 8.0
HEADING_1_FONT_SIZE = 20.0
HEADING_2_FONT_SIZE = 18.0
HEADING_3_FONT_SIZE = 16.0
NORMAL_FONT_SIZE = 12.0
CODE_FONT_SIZE = 10.0
EPSILON = 0.1


def update_heading(
    p: Paragraph,
    heading_1: Heading = None,
    heading_2: Heading = None,
    heading_3: Heading = None,
):
    if abs(p.font_size - HEADING_1_FONT_SIZE) < EPSILON:
        next_heading = Heading(title=p.text, level=0, page_number=0)
        return next_heading, None, None
    elif abs(p.font_size - HEADING_2_FONT_SIZE) < EPSILON:
        next_heading = Heading(title=p.text, level=1, page_number=0)
        return heading_1, next_heading, None
    elif abs(p.font_size - HEADING_3_FONT_SIZE) < EPSILON:
        next_heading = Heading(title=p.text, level=2, page_number=0)
        return heading_1, heading_2, next_heading
    return heading_1, heading_2, heading_3


def extract_paragraph(
    words: list[dict[str, Any]],
    page_number: int,
    page_start: int,
    headings: list[Heading],
) -> Generator[Paragraph, None, None]:
    """
    Extract paragraph from a set of words
    """
    if len(words) == 0:
        pass

    position_y = words[0].get("top")
    paragraph: list[str] = []  # list of lines
    line: str = ""
    line_number = 0
    p_start_line = line_number
    font_size = words[0].get("height")
    heading_1, heading_2, heading_3 = headings

    for w in words:
        # Add a word to the current line if it is in the same line
        if w.get("top") == position_y:
            line += w.get("text") + " "
        # Process a word in a new line
        elif w.get("top") != position_y:
            line = line.strip()
            line_number += 1

            # Add a line into the current paragraph if
            # it is not the header or footer line
            if line != HEADER and FOOTER not in line:
                paragraph.append(line)

            # Encounter a paragraph break
            if w.get("top") - position_y >= LINE_SPACE:
                # Skip paragraph break for some special words
                if line in ("Note", "Warning", "Important"):
                    pass
                # Skip paragraph break for headings
                elif (
                    font_size > NORMAL_FONT_SIZE
                    and abs(w.get("height") - font_size) < EPSILON
                ):
                    pass
                # Skip paragraph break for code block
                elif (
                    abs(font_size - CODE_FONT_SIZE) < EPSILON
                    and abs(w.get("height") - font_size) < EPSILON
                ):
                    pass
                else:
                    # Generate a paragraph
                    if paragraph:
                        p = Paragraph(
                            text=(
                                "\n".join(paragraph)
                                if abs(font_size - CODE_FONT_SIZE) < EPSILON
                                else " ".join(paragraph)
                            ),
                            font_size=font_size,
                            page=page_number - page_start + 1,
                            line=p_start_line,
                        )
                        # Update heading
                        if font_size >= (HEADING_3_FONT_SIZE - EPSILON):
                            heading_1, heading_2, heading_3 = update_heading(
                                p,
                                heading_1,
                                heading_2,
                                heading_3,
                            )
                        p.heading_1 = (
                            heading_1.title if heading_1 is not None else None
                        )
                        p.heading_2 = (
                            heading_2.title if heading_2 is not None else None
                        )
                        p.heading_3 = (
                            heading_3.title if heading_3 is not None else None
                        )

                        yield p
                        paragraph = []

                    p_start_line = line_number

            font_size = w.get("height")
            line = w.get("text") + " "
            position_y = w.get("top")

    # It is a footer
    if line:
        if FOOTER in line:
            line = ""

    headings[0] = heading_1
    headings[1] = heading_2
    headings[2] = heading_3


def extract(pdf_path: str) -> Generator[Paragraph, None, None]:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError()

    with pdfplumber.open(pdf_path) as pdf:
        _, page_start = extract_index.extract(pdf_path)
        # index, page_start = [], 24
        PAGE_START = page_start + 1
        headings = [None, None, None]

        for page_number, page in enumerate(pdf.pages):
            if page_number < PAGE_START:
                continue
            logger.info("Processing page %d", page_number + 1)

            words = page.extract_words()
            yield from extract_paragraph(
                words, page_number, PAGE_START, headings
            )
