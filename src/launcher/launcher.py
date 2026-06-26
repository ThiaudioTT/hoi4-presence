import os
import subprocess
import sys

# The Paradox launcher spawns this exe directly (no shell) with cwd = its own
# folder, and prepends its own args (session token, account id, ...). It can't
# spawn a .bat directly (EFTYPE), so this shim just runs runRPC.bat from the
# game folder via the shell, with the arg order we control.
# TODO: since we running a exe now, theres no need for a bat file anymore
gameDir = os.path.dirname(os.path.abspath(sys.argv[0]))
subprocess.Popen("runRPC.bat", cwd=gameDir, shell=True)
