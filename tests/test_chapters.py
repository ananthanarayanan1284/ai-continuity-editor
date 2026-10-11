"""Offline tests for splitting books into chapters and chapters into chunks."""

from continuity_editor.extraction.chapters import chunk_text, split_chapters, strip_gutenberg

BOOK = """\
*** START OF THE PROJECT GUTENBERG EBOOK TEST ***
Contents

 Chapter I. The Storm
 Chapter II. The Road

Chapter I
The Storm


It was a dark night. The wind
howled over the prairie.

Mira shut the door.

Chapter II
The Road


The road was long.
*** END OF THE PROJECT GUTENBERG EBOOK TEST ***
Licence text that must not appear.
"""


def test_gutenberg_header_and_footer_are_removed():
    body = strip_gutenberg(BOOK)
    assert "START OF" not in body
    assert "Licence text" not in body


def test_table_of_contents_is_skipped_and_titles_are_found():
    chapters = split_chapters(strip_gutenberg(BOOK))
    assert [(c.number, c.title) for c in chapters] == [(1, "The Storm"), (2, "The Road")]


def test_wrapped_lines_become_one_line_per_paragraph():
    first = split_chapters(strip_gutenberg(BOOK))[0]
    assert first.text == "It was a dark night. The wind howled over the prairie.\n\nMira shut the door."


def test_arabic_numbers_and_titles_on_the_heading_line():
    text = "CHAPTER 1. Arrival\n\nShe came.\n\nCHAPTER 12\n\nNo title here, just text that goes on.\n"
    chapters = split_chapters(text)
    assert [(c.number, c.title) for c in chapters] == [(1, "Arrival"), (12, "")]
    assert chapters[1].text == "No title here, just text that goes on."


def test_roman_numerals():
    text = "Chapter XIV\nThe Monkeys\n\nThey flew.\n\nChapter XIX\nTrees\n\nThey fought.\n"
    assert [c.number for c in split_chapters(text)] == [14, 19]


def test_chunks_keep_whole_paragraphs_under_the_limit():
    text = "\n\n".join([" ".join(["word"] * 300)] * 4)
    assert [len(chunk.split()) for chunk in chunk_text(text, max_words=700)] == [600, 600]


def test_a_paragraph_longer_than_the_limit_stays_whole():
    assert len(chunk_text(" ".join(["word"] * 1000), max_words=100)) == 1
