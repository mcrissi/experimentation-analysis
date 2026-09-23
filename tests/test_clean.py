"""Silver-layer tests on a tiny synthetic fixture (values invented; no network)."""

from pathlib import Path

import pandas as pd
import pytest

from xpa.data.clean import ARMS, HISTORY_SEGMENTS, SchemaError, build_silver, clean

FIXTURE = Path(__file__).parent / "fixtures" / "hillstrom_tiny.csv"


@pytest.fixture
def raw() -> pd.DataFrame:
    return pd.read_csv(FIXTURE)


def test_dtypes(raw):
    df = clean(raw)
    assert df["recency"].dtype == "int8"
    assert df["history"].dtype == "float64"
    assert df["spend"].dtype == "float64"
    for col in ("mens", "womens", "newbie"):
        assert df[col].dtype == "bool"
    for col in ("visit", "conversion"):
        assert df[col].dtype == "int8"
    for col in ("history_segment", "zip_code", "channel", "segment", "arm"):
        assert isinstance(df[col].dtype, pd.CategoricalDtype), col


def test_arm_mapping(raw):
    df = clean(raw)
    expected = {"Mens E-Mail": "mens", "Womens E-Mail": "womens", "No E-Mail": "control"}
    assert (df["arm"].astype(str) == df["segment"].astype(str).map(expected)).all()
    assert list(df["arm"].cat.categories) == list(ARMS) == ["control", "mens", "womens"]


def test_arm_ignores_past_purchase_flags(raw):
    # `mens`/`womens` are pre-treatment purchase history, not assignment.
    row = raw[(raw["segment"] == "Mens E-Mail") & (raw["mens"] == 0)]
    assert not row.empty
    assert (clean(row)["arm"] == "mens").all()


def test_history_segment_is_ordered(raw):
    cat = clean(raw)["history_segment"].dtype
    assert cat.ordered
    assert list(cat.categories) == list(HISTORY_SEGMENTS)
    assert len(HISTORY_SEGMENTS) == 7


def test_missing_column_raises(raw):
    with pytest.raises(SchemaError, match="spend"):
        clean(raw.drop(columns="spend"))


def test_unknown_segment_raises(raw):
    raw.loc[0, "segment"] = "Kids E-Mail"
    with pytest.raises(SchemaError, match="segment"):
        clean(raw)


def test_out_of_domain_binary_raises(raw):
    raw.loc[0, "visit"] = 2
    with pytest.raises(SchemaError, match="visit"):
        clean(raw)


def test_negative_spend_raises(raw):
    raw.loc[0, "spend"] = -1.0
    with pytest.raises(SchemaError, match="spend"):
        clean(raw)


def test_nulls_raise(raw):
    raw.loc[0, "history"] = None
    with pytest.raises(SchemaError, match="null"):
        clean(raw)


def test_build_silver_roundtrip(tmp_path):
    raw_dir, processed_dir = tmp_path / "raw", tmp_path / "processed"
    raw_dir.mkdir()
    (raw_dir / "hillstrom.csv").write_bytes(FIXTURE.read_bytes())

    counts = build_silver(raw_dir, processed_dir)

    df = pd.read_parquet(processed_dir / "hillstrom.parquet")
    assert counts == {"control": 3, "mens": 3, "womens": 3}
    assert isinstance(df["arm"].dtype, pd.CategoricalDtype)
    assert df["history_segment"].dtype.ordered
    assert len(df) == 9
