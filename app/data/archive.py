"""Parquet archive and rebuild (Part 13.3).

Task contract (Part 17.1):

    LAYER             layer 7
    INPUTS            a trusted batch
    OUTPUTS           partitioned Parquet files
    VALIDATION        a fresh database rebuilds from the archive alone
    FAILURE BEHAVIOR  Archive failure never invalidates an otherwise good run; it is
                      recorded and retried.
"""

from __future__ import annotations


def archive_batch(run_id: str):
    """Partition by report/year/month. Avoid thousands of tiny files.
    """
    raise NotImplementedError(
        "Not implemented yet. See this module's task contract "
        "and the constitution Part it names."
    )
