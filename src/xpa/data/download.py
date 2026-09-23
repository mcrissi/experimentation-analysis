"""Bronze layer: fetch the Hillstrom CSV into data/raw/ and record a MANIFEST.json.

Each source pins the sha256 of the CSV bytes it serves (after gunzip for .gz sources).
The two public copies hold identical values but differ in formatting (CRLF, number
formatting), so their hashes differ; see docs/decisions/0002-data-source.md.
"""

import csv
import gzip
import hashlib
import io
import json
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

CSV_NAME = "hillstrom.csv"
MANIFEST_NAME = "MANIFEST.json"


@dataclass(frozen=True)
class Source:
    name: str
    url: str
    sha256: str
    gzipped: bool = False


SOURCES: list[Source] = [
    Source(
        name="minethatdata",
        url="http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv",
        sha256="0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece",
    ),
    Source(
        name="sklift-s3-mirror",
        url="https://hillstorm1.s3.us-east-2.amazonaws.com/hillstorm_no_indices.csv.gz",
        sha256="00a6a868e05a9ffe7382da51629f6d6dce88c5acfc945e79d314ebc78fd3a2c0",
        gzipped=True,
    ),
]


class DownloadError(RuntimeError):
    pass


def _fetch(src: Source, timeout: float) -> bytes:
    with urllib.request.urlopen(src.url, timeout=timeout) as resp:
        payload = resp.read()
    return gzip.decompress(payload) if src.gzipped else payload


def download(raw_dir: Path, sources: list[Source] | None = None, timeout: float = 60.0) -> dict:
    """Try each source in order; write the first one whose checksum matches."""
    sources = SOURCES if sources is None else sources
    failures: dict[str, str] = {}

    for src in sources:
        try:
            data = _fetch(src, timeout)
        except Exception as exc:
            failures[src.name] = f"fetch failed: {exc}"
            continue
        digest = hashlib.sha256(data).hexdigest()
        if digest != src.sha256:
            failures[src.name] = f"checksum mismatch: got {digest}, expected {src.sha256}"
            continue

        rows = list(csv.reader(io.StringIO(data.decode("utf-8"))))
        manifest = {
            "source_name": src.name,
            "source_url": src.url,
            "retrieved_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "sha256": digest,
            "bytes": len(data),
            "n_rows": len(rows) - 1,
            "columns": rows[0],
            "failed_sources": failures,
        }
        raw_dir.mkdir(parents=True, exist_ok=True)
        tmp = raw_dir / f"{CSV_NAME}.part"
        tmp.write_bytes(data)
        tmp.replace(raw_dir / CSV_NAME)
        (raw_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2) + "\n")
        return manifest

    detail = "; ".join(f"{name}: {why}" for name, why in failures.items())
    raise DownloadError(f"all sources failed ({detail})")
