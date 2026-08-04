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
    """These names are referenced as strings by runRPC.bat and the updater."""
    assert {name for _, name, _ in buildSpecTargets} == EXPECTED_EXES


def test_the_presence_has_no_console_window(buildSpecTargets):
    console = {name: hasConsole for _, name, hasConsole in buildSpecTargets}

    assert console["hoi4Presence"] is False
    assert console["runRPC"] is False
    assert console["setup"] is True


def test_required_dist_files_match_what_the_build_produces(buildSpecTargets):
    """The installer's checklist and the build output must not drift apart."""
    payloadExes = {f"{name}.exe" for _, name, _ in buildSpecTargets} - {"setup.exe", "uninstall.exe"}

    assert set(REQUIRED_DIST_FILES) == payloadExes | {"runRPC.bat", "version.json"}


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


def test_workflows_reference_the_licence_file_that_exists(repoRoot):
    """The on-disk file is LICENSE.TXT; a lowercase reference only works by luck."""
    for workflow in (repoRoot / ".github" / "workflows").glob("*.yaml"):
        text = workflow.read_text(encoding="utf-8")
        assert "LICENSE.txt" not in text, f"{workflow.name} references LICENSE.txt, but the file is LICENSE.TXT"
