"""Layers 1-2: authorized Excel access and block extraction (Parts 7, 23.5).

Only `com_adapter` and `session` may import COM. Everything downstream
depends on `port.ExtractionPort` so the pipeline stays testable off
Windows (Part 44.2).
"""
