"""Entry point for runRPC.exe -- the shim the Paradox launcher spawns.

The launcher starts this executable directly (no shell) with cwd set to its own
folder, and prepends its own arguments (session token, account id, ...). It
cannot spawn a .bat directly, so this shim runs runRPC.bat from the game folder
via the shell, with the argument order we control.
"""

from __future__ import annotations

import os
import subprocess
import sys

BATCH_NAME = "runRPC.bat"


def main() -> int:
    gameDir = os.path.dirname(os.path.abspath(sys.argv[0]))
    subprocess.Popen(BATCH_NAME, cwd=gameDir, shell=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
