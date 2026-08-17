"""Environment paths and safe defaults (Part 30.7 rule 3).

Task contract (Part 17.1):

    LAYER             all layers
    INPUTS            environment + operator config
    OUTPUTS           resolved, validated, user-writable paths
    VALIDATION        user data and config live OUTSIDE the versioned application folder so an upgrade cannot overwrite them
    FAILURE BEHAVIOR  An unwritable or unapproved path fails closed at startup rather than
                      writing somewhere convenient.
"""

from __future__ import annotations


def resolve_paths():
    """Unicode-safe, normalized absolute paths. Test paths with spaces,
    Arabic characters and long names (Part 30.7 rule 4).
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
