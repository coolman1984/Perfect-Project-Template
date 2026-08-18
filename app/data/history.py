"""The history engine (Part 8).

Task contract (Part 17.1):

    LAYER             layer 6
    INPUTS            validated clean rows + load mode
    OUTPUTS           inserted / updated / unchanged / rejected counts
    VALIDATION        rerunning identical input creates zero duplicates (rule 5)
    FAILURE BEHAVIOR  Any failure rolls the transaction back and leaves trusted history
                      exactly as it was (Part 8.5).
"""

from __future__ import annotations


def apply(rows: object, load_mode: str):
    """append | upsert | snapshot | replace_period. business_key_hash
    answers 'same record?'; row_content_hash answers 'did it change?'
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )

def apply_deletion_rule(missing_keys: object, rule: str):
    """ignore | mark_inactive | soft_delete | close_version | physical.
    Never infer what a disappearing row means (Part 8.4).
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
