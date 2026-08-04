"""Logging for executables that may not have a console.

``hoi4Presence.exe`` and ``runRPC.exe`` are built with ``console=False``, so
anything printed by them is discarded. Every diagnostic therefore goes to a log
file next to the executable as well as to stderr.
"""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

LOG_FILE_NAME = "hoi4Presence.log"
MAX_BYTES = 1024 * 1024
BACKUP_COUNT = 3
LOG_FORMAT = "%(asctime)s %(levelname)-8s %(name)s: %(message)s"


def setupLogging(
    baseDir: str | os.PathLike[str],
    *,
    level: int = logging.INFO,
    fileName: str = LOG_FILE_NAME,
) -> logging.Logger:
    """Configure the root logger to write to ``baseDir/fileName`` and stderr.

    A failure to open the log file is not fatal: the presence should still run
    from a read-only folder, just without a log.
    """
    root = logging.getLogger()
    root.setLevel(level)
    for existing in list(root.handlers):
        root.removeHandler(existing)

    formatter = logging.Formatter(LOG_FORMAT)

    stream = logging.StreamHandler(sys.stderr)
    stream.setFormatter(formatter)
    root.addHandler(stream)

    try:
        fileHandler = RotatingFileHandler(
            os.path.join(baseDir, fileName),
            maxBytes=MAX_BYTES,
            backupCount=BACKUP_COUNT,
            encoding="utf-8",
        )
    except OSError:
        root.warning("Could not open the log file in %s; logging to stderr only.", baseDir)
    else:
        fileHandler.setFormatter(formatter)
        root.addHandler(fileHandler)

    return root
