"""Evidence-first insight generation (Parts 10.3, 26.6).

Task contract (Part 17.1):

    LAYER             layer 8
    INPUTS            verified metric results
    OUTPUTS           ranked evidence objects, then sentences from templates
    VALIDATION        every insight can show the numbers behind it
    FAILURE BEHAVIOR  With no verified evidence, produce no insight. Silence beats a
                      confident invented cause.
"""

from __future__ import annotations


def build_evidence(period: str):
    """Build the Part 26.6 evidence object BEFORE any text exists.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )

def rank(candidates: object):
    """impact x magnitude x persistence x population x confidence. Show at
    most five (Part 10.3).
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )

def narrate(evidence: object):
    """Deterministic sentence templates. Optional approved AI may improve
    wording only — never numbers and never causal claims.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
