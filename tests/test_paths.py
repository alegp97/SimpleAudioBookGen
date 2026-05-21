from pathlib import Path
import os

import pytest

from audiobook_gen import main
from audiobook_gen.paths import APP_NAME, user_data_dir


@pytest.mark.skipif(os.name != "nt", reason="Windows app data path")
def test_user_data_dir_uses_localappdata_on_windows(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))

    assert user_data_dir() == tmp_path / APP_NAME


def test_frozen_config_path_is_user_writable(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "is_frozen", lambda: True)
    monkeypatch.setattr(main, "ensure_user_data_dir", lambda: tmp_path)

    assert main.config_path() == tmp_path / "config.yaml"


def test_frozen_relative_log_path_is_user_writable(monkeypatch, tmp_path):
    monkeypatch.setattr(main, "is_frozen", lambda: True)
    monkeypatch.setattr(main, "ensure_user_data_dir", lambda: tmp_path)

    assert main.log_path("audiobook_gen.log") == str(tmp_path / "audiobook_gen.log")


def test_absolute_log_path_is_preserved(monkeypatch, tmp_path):
    log_file = Path(tmp_path) / "custom.log"
    monkeypatch.setattr(main, "is_frozen", lambda: True)

    assert main.log_path(str(log_file)) == str(log_file)
