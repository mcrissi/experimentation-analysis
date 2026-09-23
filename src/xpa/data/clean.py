"""Silver layer: typed Parquet with an `arm` column and schema assertions.

`arm` comes from `segment` only. The `mens`/`womens` flags are pre-treatment purchase
history (bought men's/women's merchandise in the past year), not the assignment.
Category labels are kept as published (including the source's "Surburban" spelling).
"""

from pathlib import Path

import pandas as pd

from xpa.data.download import CSV_NAME

SILVER_NAME = "hillstrom.parquet"

ARMS = ("control", "mens", "womens")
SEGMENT_TO_ARM = {"No E-Mail": "control", "Mens E-Mail": "mens", "Womens E-Mail": "womens"}
HISTORY_SEGMENTS = (
    "1) $0 - $100",
    "2) $100 - $200",
    "3) $200 - $350",
    "4) $350 - $500",
    "5) $500 - $750",
    "6) $750 - $1,000",
    "7) $1,000 +",
)
ZIP_CODES = ("Rural", "Surburban", "Urban")
CHANNELS = ("Multichannel", "Phone", "Web")

COLUMNS = (
    "recency",
    "history_segment",
    "history",
    "mens",
    "womens",
    "zip_code",
    "newbie",
    "channel",
    "segment",
    "visit",
    "conversion",
    "spend",
)
BINARY = ("mens", "womens", "newbie", "visit", "conversion")
CATEGORIES = {
    "history_segment": HISTORY_SEGMENTS,
    "zip_code": ZIP_CODES,
    "channel": CHANNELS,
    "segment": tuple(SEGMENT_TO_ARM),
}


class SchemaError(ValueError):
    pass


def _check_raw(df: pd.DataFrame) -> None:
    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise SchemaError(f"missing columns: {missing}")
    nulls = df[list(COLUMNS)].isna().sum()
    if nulls.any():
        raise SchemaError(f"null values: {nulls[nulls > 0].to_dict()}")
    for col, allowed in CATEGORIES.items():
        bad = set(df[col].unique()) - set(allowed)
        if bad:
            raise SchemaError(f"unexpected {col} values: {sorted(bad)}")
    for col in BINARY:
        bad = set(df[col].unique()) - {0, 1}
        if bad:
            raise SchemaError(f"{col} must be 0/1, got {sorted(bad)}")
    if not df["recency"].between(1, 12).all():
        raise SchemaError("recency must be in 1..12")
    if not (df["history"] > 0).all():
        raise SchemaError("history must be > 0")
    if (df["spend"] < 0).any():
        raise SchemaError("spend must be >= 0")


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    """Validate the raw table and return typed columns plus `arm`."""
    _check_raw(raw)
    df = pd.DataFrame(
        {
            "recency": raw["recency"].astype("int8"),
            "history_segment": pd.Categorical(
                raw["history_segment"], categories=HISTORY_SEGMENTS, ordered=True
            ),
            "history": raw["history"].astype("float64"),
            "mens": raw["mens"].astype(bool),
            "womens": raw["womens"].astype(bool),
            "zip_code": pd.Categorical(raw["zip_code"], categories=ZIP_CODES),
            "newbie": raw["newbie"].astype(bool),
            "channel": pd.Categorical(raw["channel"], categories=CHANNELS),
            "segment": pd.Categorical(raw["segment"], categories=tuple(SEGMENT_TO_ARM)),
            "arm": pd.Categorical(raw["segment"].map(SEGMENT_TO_ARM), categories=ARMS),
            "visit": raw["visit"].astype("int8"),
            "conversion": raw["conversion"].astype("int8"),
            "spend": raw["spend"].astype("float64"),
        }
    )
    if df["arm"].isna().any():
        raise SchemaError("arm could not be derived for some rows")
    return df


def build_silver(raw_dir: Path, processed_dir: Path) -> dict[str, int]:
    """Write the silver Parquet; return row counts per arm (sizes only, no outcomes)."""
    df = clean(pd.read_csv(raw_dir / CSV_NAME))
    processed_dir.mkdir(parents=True, exist_ok=True)
    df.to_parquet(processed_dir / SILVER_NAME, index=False)
    return {arm: int(n) for arm, n in df["arm"].value_counts(sort=False).items()}
