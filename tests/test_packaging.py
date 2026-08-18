"""Repository consistency checks that do not need PyInstaller or Windows.

The Windows build cannot run on Linux CI, so these guard the parts of it that
can be checked statically -- above all that build.spec still points at scripts
that exist, which is the failure mode a package move causes.
"""

from __future__ import annotations

import ast

import pytest

from hoi4presence.install.steps import REQUIRED_DIST_FILES

ENTRYPOINT_NAMES = ["hoi4RPC.py", "checkupdate.py", "launcher.py", "installer.py", "uninstaller.py"]

EXPECTED_EXES = {"hoi4Presence", "checkupdate", "runRPC", "setup", "uninstall"}


def test_build_spec_entry_scripts_exist(repoRoot, buildSpecTargets):
    """A moved module must not silently break the release build."""
    missing = [script for script, _, _ in buildSpecTargets if not (repoRoot / "src" / "entrypoints" / script).is_file()]

    assert not missing, f"build.spec references entry scripts that do not exist: {missing}"


def test_build_spec_builds_every_entrypoint(buildSpecTargets):
    assert {script for script, _, _ in buildSpecTargets} == set(ENTRYPOINT_NAMES)


def test_build_spec_exe_names_are_unchanged(buildSpecTargets):
    """These names are referenced as strings by the shim and the updater."""
    assert {name for _, name, _ in buildSpecTargets} == EXPECTED_EXES


def test_the_presence_has_no_console_window(buildSpecTargets):
    console = {name: hasConsole for _, name, hasConsole in buildSpecTargets}

    assert console["hoi4Presence"] is False
    assert console["runRPC"] is False
    assert console["setup"] is True


def test_required_dist_files_match_what_the_build_produces(buildSpecTargets):
    """The installer's checklist and the build output must not drift apart."""
    payloadExes = {f"{name}.exe" for _, name, _ in buildSpecTargets} - {"setup.exe", "uninstall.exe"}

    assert set(REQUIRED_DIST_FILES) == payloadExes | {"version.json"}


@pytest.mark.parametrize("scriptName", ENTRYPOINT_NAMES)
def test_entry_scripts_do_their_work_inside_main(repoRoot, scriptName):
    """Importing an entry point must not run it.

    The presence used to connect to Discord and loop at import time, and
    checkupdate called checkUpdate() on the last line, which is why none of this
    could be tested at all.
    """
    tree = ast.parse((repoRoot / "src" / "entrypoints" / scriptName).read_text(encoding="utf-8"))

    functions = {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}
    assert "main" in functions, f"{scriptName} has no main()"

    guards = [node for node in tree.body if isinstance(node, ast.If) and "__main__" in ast.dump(node.test)]
    assert guards, f"{scriptName} has no `if __name__ == '__main__'` guard"

    stray = [node for node in tree.body if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)]
    assert not stray, f"{scriptName} calls something at import time (line {stray[0].lineno})"


def test_the_release_asset_name_matches_the_build_output(repoRoot):
    """build.spec's zip name and the updater's expected asset name must agree.

    They only line up when a release tag is exactly "v<version>", which is the
    convention this asserts. See the known-issues note in AGENTS.md.
    """
    import json

    from hoi4presence.updater.release import assetName

    version = json.loads((repoRoot / "version.json").read_text(encoding="utf-8"))["version"]
    spec = (repoRoot / "build.spec").read_text(encoding="utf-8")

    assert 'f"hoi4-presence-v{version}.zip"' in spec
    assert assetName(f"v{version}") == f"hoi4-presence-v{version}.zip"


def test_the_shim_agrees_with_the_names_everything_else_uses(repoRoot):
    """launcher.py duplicates these rather than importing them.

    That is deliberate -- it is the first link in the launch chain and stays
    stdlib-only -- but it makes the duplication the one coupling in the chain
    nothing else enforces. A rename in steps.py or paths.py that misses the shim
    leaves the game starting and the presence silently never showing up.
    """
    import hoi4presence.paths as paths
    from hoi4presence.install import steps

    tree = ast.parse((repoRoot / "src" / "entrypoints" / "launcher.py").read_text(encoding="utf-8"))
    shim = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            try:
                shim[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass

    assert shim["CONFIG_NAME"] == steps.CONFIG_NAME
    assert shim["UPDATER_EXE"] == steps.UPDATER_EXE
    assert shim["PRESENCE_EXE"] == steps.PRESENCE_EXE
    assert shim["GAME_EXE"] == paths.GAME_EXE
    assert shim["INSTALL_DIR_NAME"] == paths.INSTALL_DIR_NAME
    # Launching through the shim must hand the game the same arguments the
    # launcher passes it when the presence is not installed.
    assert shim["GAME_ARGS"] == list(steps.VANILLA_LAUNCHER[1])
    assert steps.VANILLA_LAUNCHER[0].endswith(shim["GAME_EXE"])


@pytest.mark.parametrize("scriptName", ["hoi4RPC.py", "launcher.py"])
def test_the_windowed_executables_do_not_import_the_console_ui(repoRoot, scriptName):
    """These two are built console=False, so there is no terminal to draw on.

    rich would render into ``NULL_FILE`` and every bar would go nowhere. Worse,
    ``launcher.py`` is deliberately stdlib-only -- it is the first link in the
    launch chain, so nothing it needs may fail to import. Flipping either exe to
    console=True is not the fix either: that puts a console window on top of the
    running game.
    """
    tree = ast.parse((repoRoot / "src" / "entrypoints" / scriptName).read_text(encoding="utf-8"))

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    assert "hoi4presence.ui" not in imported, f"{scriptName} has no console to render a UI into"


def test_no_batch_file_is_left_in_the_launch_chain(repoRoot):
    """The shim runs the game itself now; cmd.exe is out of the chain.

    A .bat reappearing means shell=True, the console codepage and CRLF line
    endings come back with it. All three were bugs; see the CHANGELOG.
    """
    assert not list((repoRoot / "src").rglob("*.bat"))


def test_workflows_reference_the_licence_file_that_exists(repoRoot):
    """The on-disk file is LICENSE.TXT; a lowercase reference only works by luck."""
    for workflow in (repoRoot / ".github" / "workflows").glob("*.yaml"):
        text = workflow.read_text(encoding="utf-8")
        assert "LICENSE.txt" not in text, f"{workflow.name} references LICENSE.txt, but the file is LICENSE.TXT"
