"""Durable progress and user-action events (Part 22.4).

Task contract (Part 17.1):

    LAYER             API + orchestrator
    INPUTS            stage changes
    OUTPUTS           ordered, replayable events validated against run_event.schema.json
    VALIDATION        a browser refresh or closure never loses progress
    FAILURE BEHAVIOR  Events are STORED BEFORE DELIVERY. The renderer can never become the
                      source of truth (Part 25.5.1 rule 6).
"""

from __future__ import annotations


def emit(run_id: str, stage: str, **fields: object):
    """Monotonic sequence per run. Clients resume with ?since=<sequence>.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )

def since(run_id: str, sequence: int):
    """Replay from durable storage, never from memory.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
