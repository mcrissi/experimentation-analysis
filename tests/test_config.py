from pathlib import Path

import pytest

from xpa.config import Settings


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch, tmp_path):
    for var in ("DATA_DIR", "XPA_DATA_DIR", "XPA_SEED"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.chdir(tmp_path)  # no stray .env


def test_defaults():
    s = Settings()
    assert s.data_dir == Path("data")
    assert s.seed == 20080320


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("DATA_DIR", "elsewhere")
    monkeypatch.setenv("XPA_SEED", "7")
    s = Settings()
    assert s.data_dir == Path("elsewhere")
    assert s.seed == 7


def test_derived_paths():
    s = Settings(data_dir=Path("d"))
    assert s.raw_dir == Path("d") / "raw"
    assert s.processed_dir == Path("d") / "processed"
