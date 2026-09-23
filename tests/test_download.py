"""Download tests against a local HTTP server (no network)."""

import gzip
import hashlib
import json
import threading
from datetime import datetime
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

from xpa.data.download import DownloadError, Source, download

CSV = b"recency,history,segment\r\n10,142.44,Womens E-Mail\r\n6,329.08,No E-Mail\r\n"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


class _QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


@pytest.fixture
def server(tmp_path):
    root = tmp_path / "www"
    root.mkdir()
    (root / "data.csv").write_bytes(CSV)
    (root / "data.csv.gz").write_bytes(gzip.compress(CSV))
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(_QuietHandler, directory=str(root)))
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()


def test_writes_csv_and_manifest(server, tmp_path):
    raw = tmp_path / "raw"
    src = Source("primary", f"{server}/data.csv", sha(CSV))

    manifest = download(raw, sources=[src])

    assert (raw / "hillstrom.csv").read_bytes() == CSV
    on_disk = json.loads((raw / "MANIFEST.json").read_text())
    assert on_disk == manifest
    assert manifest["source_name"] == "primary"
    assert manifest["source_url"] == src.url
    assert manifest["sha256"] == sha(CSV)
    assert manifest["n_rows"] == 2
    assert manifest["columns"] == ["recency", "history", "segment"]
    assert datetime.fromisoformat(manifest["retrieved_at"]).tzinfo is not None


def test_checksum_mismatch_falls_back_to_next_source(server, tmp_path):
    raw = tmp_path / "raw"
    bad = Source("primary", f"{server}/data.csv", "0" * 64)
    mirror = Source("mirror", f"{server}/data.csv.gz", sha(CSV), gzipped=True)

    manifest = download(raw, sources=[bad, mirror])

    assert manifest["source_name"] == "mirror"
    assert (raw / "hillstrom.csv").read_bytes() == CSV
    assert "checksum mismatch" in manifest["failed_sources"]["primary"]


def test_all_sources_fail_raises_and_leaves_no_csv(server, tmp_path):
    raw = tmp_path / "raw"
    bad = Source("primary", f"{server}/data.csv", "0" * 64)
    missing = Source("mirror", f"{server}/nope.csv", sha(CSV))

    with pytest.raises(DownloadError) as exc:
        download(raw, sources=[bad, missing])

    assert "primary" in str(exc.value) and "mirror" in str(exc.value)
    assert not (raw / "hillstrom.csv").exists()
    assert not (raw / "MANIFEST.json").exists()


def test_default_sources_pin_a_sha256_each():
    from xpa.data.download import SOURCES

    assert len(SOURCES) >= 2
    for s in SOURCES:
        assert len(s.sha256) == 64
        int(s.sha256, 16)
    assert Path(SOURCES[0].url).name.endswith(".csv")


def test_manifest_uses_lf_line_endings(server, tmp_path):
    raw = tmp_path / "raw"
    download(raw, sources=[Source("primary", f"{server}/data.csv", sha(CSV))])
    assert b"\r" not in (raw / "MANIFEST.json").read_bytes()
