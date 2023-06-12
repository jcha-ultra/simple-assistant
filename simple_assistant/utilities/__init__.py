from datetime import datetime
from importlib import import_module
import os
from pathlib import Path
from types import ModuleType

def generate_timestamp_id():
    """
    Generate a timestamp ID in the format of YYYY-MM-DD-HHMM-SS-NNNNNN.
    """
    return datetime.utcnow().strftime('%Y-%m-%d_%H%M-%S-%f')


def quick_import(location: Path) -> ModuleType:
    """Import a module directly from a Path."""
    return import_module(str(location.with_suffix("")).replace(os.path.sep, "."))
