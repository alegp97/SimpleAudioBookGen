import sys
import os
from pathlib import Path

# Añadir la raíz del proyecto al path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import pytest
from audiobook_gen.config import Settings

@pytest.fixture
def settings():
    """Fixture que proporciona una instancia de Settings para tests."""
    return Settings(debug=True)
