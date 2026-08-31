import os
import sys
import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


@pytest.fixture(autouse=True)
def test_db():
    import src.models.database as db_module
    db_module._engine = None
    db_module._session_factory = None
    original_get_db_path = db_module._get_db_path
    test_db_path = Path(__file__).parent / "tests" / "test_sanglow.db"
    test_db_path.parent.mkdir(parents=True, exist_ok=True)
    db_module._get_db_path = lambda: test_db_path
    db_module.init_db()
    yield
    db_module._get_db_path = original_get_db_path
    db_module._engine = None
    db_module._session_factory = None
    if test_db_path.exists():
        try:
            test_db_path.unlink()
        except Exception:
            pass
