"""Single writer of every parquet the project publishes.

Every parameter is explicit, none is left to a default. Byte reproducibility
is a criterion of the story, and a default that changes in a minor release of
polars would break it without anybody touching the generator.
"""

from pathlib import Path
from typing import Final, Literal

import polars as pl

COMPRESSION: Final[Literal["zstd"]] = "zstd"
COMPRESSION_LEVEL: Final[int] = 3
ROW_GROUP_SIZE: Final[int] = 250_000


def write_frozen_parquet(frame: pl.DataFrame, path: Path) -> int:
    """Write a frame with the frozen format of the project.

    Args:
        frame: Frame to write.
        path: Destination file; its parent is created if needed.

    Returns:
        The size of the written file in bytes.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(
        path,
        compression=COMPRESSION,
        compression_level=COMPRESSION_LEVEL,
        row_group_size=ROW_GROUP_SIZE,
        statistics=True,
    )
    return path.stat().st_size
