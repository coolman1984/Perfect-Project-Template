"""DuckDB connection and transaction policy (Part 23.3).

Task contract (Part 17.1):

    LAYER             layer 3-8
    INPUTS            configuration
    OUTPUTS           a connection with one coordinated writer
    VALIDATION        memory_limit, temp_directory, max_temp_directory_size and threads are set from measured workloads
    FAILURE BEHAVIOR  Fail early if RAM or disk is unsafe, before extraction starts.
"""

from __future__ import annotations


def connect(read_only: bool = False):
    """One coordinated writer per database file. Disable DuckDB extension
    autoinstall and autoload (Part 23.6).
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
