# Copyright (c) 2007-2024 Yüce Tekol and PySwip Contributors
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import Union
from pathlib import Path
import re


def resolve_path(path: Union[str, Path], relative_to: Union[str, Path] = "") -> Path:
    path = Path(path).expanduser()
    if path.is_absolute() or not relative_to:
        return path
    relative_to = Path(relative_to).expanduser()
    if relative_to.is_symlink():
        raise ValueError("Symbolic links are not supported")
    if relative_to.is_dir():
        return relative_to / path
    elif relative_to.is_file():
        return relative_to.parent / path
    raise ValueError("relative_to must be either a filename or a directory")

def validate_swipl_flag(key, value):
    """
    Validates a SWI-Prolog flag key and value according to https://www.swi-prolog.org/pldoc/man?section=flags
    Returns True if valid, False otherwise.
    """
    if not isinstance(key, str) or not key:
        return False
    if not re.match(r'^[A-Za-z0-9_-]+$', key):
        return False

    # Flag type mapping: only flags supported as command-line options in SWI-Prolog
    flag_types = {
        # bool flags (can be --flag or --flag=true/false)
        "debug": "bool",
        "signals": "bool",
        "packs": "bool",
        "threads": "bool",
        "xpce": "bool",
        "traditional": "bool",
        "quiet": "bool",
        "tty": "bool",
        "debug-on-interrupt": "bool",
        "pce": "bool",
        # integer flags (with units)
        "stack-limit": "int_unit",
        "table-space": "int_unit",
        "shared-table-space": "int_unit",
        # integer flags (no units)
        "pldoc": "int",
        # atom flags
        "home": "atom",  # --home=/path/to/swipl
    }

    t = flag_types.get(key)
    if t == "bool":
        return isinstance(value, bool)
    if t == "int_unit":
        if isinstance(value, int):
            return value >= 0
        if isinstance(value, str):
            # Accept e.g. '1000000K', '512M', '1G', '2048B'
            if re.match(r'^[0-9]+([KMG]|B)?$', value, re.IGNORECASE):
                return True
        return False
    if t == "int":
        if isinstance(value, int):
            return value >= 0
        if isinstance(value, str):
            # Only accept pure digits for int flags without units
            if re.match(r'^[0-9]+$', value):
                return True
        return False
    if isinstance(t, list):
        return isinstance(value, str) and value in t
    # Accept string/atom for atom flags
    if t == "atom":
        return isinstance(value, str)
    return False