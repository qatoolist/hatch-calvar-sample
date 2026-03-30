# SPDX-FileCopyrightText: 2026-present QAToolist <qatoolist@gmail.com>
#
# SPDX-License-Identifier: MIT
"""Version metadata for hatch_calvar_sample package."""

import re
from importlib.metadata import version as _version_func
from pathlib import Path

try:
    __version__ = _version_func("hatch-calvar-sample")
except Exception:
    _version_file = Path(__file__).parent / "VERSION"
    if _version_file.exists():
        _match = re.search(r'"([^"]+)"', _version_file.read_text())
        __version__ = _match.group(1) if _match else "0.0.0.dev1"
    else:
        __version__ = "0.0.0.dev1"
