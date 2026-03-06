"""Compatibility database layer.

This module exposes database helpers from services.db so project can use
`database.db` path in a clean architecture style.
"""

from services.db import *  # noqa: F401,F403
