from pydantic import BaseModel


class Heading(BaseModel):
    title: str
    level: int
    page_number: int


class Paragraph(BaseModel):
    text: str
    font_size: float = 12
    heading_1: str | None = None
    heading_2: str | None = None
    heading_3: str | None = None
    page: int
    line: int


class Index:
    pass
