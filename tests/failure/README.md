# Failure tests

Constitution Part 15: **trusted history must survive all of them.**

```text
Excel closes mid-run · missing column · duplicate key · disk low
SQL disconnect · cancel · crash before commit · corrupt package
missing required component · port occupied · browser refresh mid-run
```

Each test asserts two things: the failure is detected, **and** the trusted
history plus the last approved dashboard are unchanged (Part 12.6).

A failure test that only checks for an exception is incomplete.
