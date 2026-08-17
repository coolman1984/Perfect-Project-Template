"""Test suite (Constitution Part 15).

Uses stdlib `unittest` so the suite runs in a bare workspace with no
third-party installs, for the same reason the tool tier is stdlib-only
(Part 37.2). A project may layer pytest on top in its QA kit; these tests are
compatible with both runners.

    python3 -m unittest discover -s tests -t .
"""
