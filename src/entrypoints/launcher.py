"""Entry point for runRPC.exe -- the shim the Paradox launcher spawns.

The launcher starts this executable directly (no shell) with cwd set to its own
folder, and prepends its own arguments (session token, account id, ...). This
shim starts the game and the presence itself, with the argument order we
control.

The names below are duplicated from ``hoi4presence.install.steps`` and
``hoi4presence.paths`` rather than imported: this is the first link in the launch
chain and is deliberately stdlib-only, so nothing it needs can fail to import.
``tests/test_packaging.py`` keeps the two copies in agreement.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

CONFIG_NAME = "runRPC.cfg"
GAME_EXE = "hoi4.exe"
INSTALL_DIR_NAME = "hoi4Presence"
UPDATER_EXE = "checkupdate.exe"
PRESENCE_EXE = "hoi4Presence.exe"

GAME_ARGS = ["-gdpr-compliant"]


def main() -> int:
    gameDir = Path(sys.argv[0]).resolve().parent

    # The game first, and outside the try: whatever else goes wrong, clicking
    # Play must still start HOI4. A missing or unreadable runRPC.cfg degrades to
    # "no presence this session", never to "the button does nothing" -- and this
    # exe is built with console=False, so there is nobody to report a failure to.
    subprocess.Popen([str(gameDir / GAME_EXE), *GAME_ARGS], cwd=gameDir)

    try:
        documents = Path((gameDir / CONFIG_NAME).read_text(encoding="utf-8").strip())
        installDir = documents / INSTALL_DIR_NAME
        for exeName in (UPDATER_EXE, PRESENCE_EXE):
            subprocess.Popen([str(installDir / exeName)], cwd=installDir)
    except OSError:
        # ponytail: a broken install is the user's cue to re-run setup.exe; the
        # presence logs nothing here because it never started.
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
