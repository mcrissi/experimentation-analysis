from typer.testing import CliRunner

from xpa import __version__
from xpa.cli import app

runner = CliRunner()


def test_download_command_uses_raw_dir_and_reports(monkeypatch, tmp_path):
    calls = {}

    def fake_download(raw_dir):
        calls["raw_dir"] = raw_dir
        return {"source_name": "primary", "sha256": "ab" * 32, "n_rows": 64000}

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setattr("xpa.cli.download", fake_download)

    result = runner.invoke(app, ["download"])

    assert result.exit_code == 0, result.output
    assert calls["raw_dir"] == tmp_path / "raw"
    assert "ab" * 32 in result.output
    assert "64000" in result.output


def test_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_clean_command_reports_arm_sizes_only(monkeypatch, tmp_path):
    calls = {}

    def fake_build_silver(raw_dir, processed_dir):
        calls["dirs"] = (raw_dir, processed_dir)
        return {"control": 3, "mens": 3, "womens": 3}

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.setattr("xpa.cli.build_silver", fake_build_silver)

    result = runner.invoke(app, ["clean"])

    assert result.exit_code == 0, result.output
    assert calls["dirs"] == (tmp_path / "raw", tmp_path / "processed")
    for arm in ("control", "mens", "womens"):
        assert arm in result.output
