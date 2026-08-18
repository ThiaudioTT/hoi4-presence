"""Shared library for the hoi4-presence executables.

Everything in this package must stay importable on any platform so the test
suite can run on Linux CI. The Windows-only and Discord-only bits live in
:mod:`hoi4presence.runner` and in the scripts under ``src/entrypoints/``.
"""
