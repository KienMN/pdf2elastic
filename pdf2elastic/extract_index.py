import logging
import re

import pdfplumber
from pdf_components import Heading

logger = logging.getLogger(__name__)

LEFT_MARGIN = 36
TAB_SIZE = 16
HEADER = "User Guide"
TABLE_OF_CONTENT = "Table of Contents"
GLOSSARY = "Glossary"  # Assume that index ends with Glossary


def extract(pdf_path: str) -> tuple[list[Heading], int]:
    """
    Extract index of a pdf file based on Table of Content
    """
    with pdfplumber.open(pdf_path) as pdf:
        index: list[Heading] = []
        for page_number, page in enumerate(pdf.pages):
            # print(f"Page {page_number + 1}:")
            logger.info("Extracting index on page %d", page_number + 1)

            title = ""
            level = 0
            page_number_word = False

            for word in page.extract_words():
                t = word.get("text")

                # Calculate level of heading based on left margin
                if not title:
                    level = int(word.get("x0") - LEFT_MARGIN) // TAB_SIZE

                # Extract ... out of title
                if "..." in t:
                    pattern = r"\w+"
                    w = re.findall(pattern, t)
                    if w:
                        title += w[0] + " "
                    page_number_word = True
                    continue

                # Extract page number
                if page_number_word:
                    if title:
                        index.append(
                            Heading(
                                title=title.strip(),
                                page_number=int(t),
                                level=level,
                            )
                        )
                    page_number_word = False
                    title = ""
                    continue

                title += t + " "

                if TABLE_OF_CONTENT in title:
                    # print("Start reading TOC")
                    logger.info("Start reading TOC")
                    title = ""
                elif HEADER in title:
                    # Skip header of a page
                    title = ""

            if len(index) > 0:
                # print(index[-1].title)
                if GLOSSARY in index[-1].title:
                    return index, page_number
    if not index:
        raise Exception("Cannot read index")
    return index, page_number
