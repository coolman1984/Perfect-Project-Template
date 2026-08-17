# Test fixtures

Synthetic and masked safe inputs only (Constitution Part 30.5).

**Never place a confidential production workbook here.** Extracted data carries
the same sensitivity as the protected source, without the DRM wrapper
(Part 13.5). If the user needs a real-data result, deliver it separately in an
access-controlled package.

`sample_production.csv` is synthetic. It exists so the fixture adapter
(Part 44) can exercise layers 3-10 on any machine. Its known control totals:

```text
rows            8
produced_qty    8060
defect_qty      100
```

Fixture-backed output is always watermarked DEMO DATA and can never satisfy
`GATE_PROTECTED_FILE_PROOF` (Part 44.3 rule 3).
