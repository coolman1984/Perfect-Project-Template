# Single product goal

This template exists to turn supplied Excel files and plain business meaning
into a finished offline application without rebuilding the shared engine.

```text
INPUT
Template ZIP + Excel files + business explanation

→ CHATGPT WORK
Understand structure and meaning
→ reuse existing capabilities
→ change configuration and mappings first
→ add small project SQL or isolated Python only when required
→ run tests and reconciliations
→ build the final offline package

→ OUTPUT
ProjectName.zip

→ FINAL USER
Extract → double-click START → browser opens → work
```

> If a non-technical user needs to understand how the engine works, the
> template has failed.

## Two packages

The template/build package is technical because ChatGPT Work is its user. It
retains source, tests, locks, maps, build inputs and every internal capability.

The operator package is for the business user. Its visible root is exactly:

```text
ProjectName/
    START.bat
    QUICK_START.html
    Application/
```

The user does not operate Python, SQL, databases, packages, terminals, Git,
configuration, migrations, agents, ports or build tools.

## Adaptation order

1. Reuse an existing capability unchanged.
2. Change project configuration or mappings.
3. Add project-owned SQL.
4. Add isolated project-owned Python only when SQL is unsuitable.
5. Change shared engine code only after evidence proves a reusable gap.

Simplifying the visible surface never removes, replaces or weakens the locked
engine, quality controls, security rules, offline dependencies or release
gates.
