# ADR 0002: Hillstrom data source for `xpa download`

- **Date:** 2026-09-23
- **Status:** accepted

## Context
`xpa download` must fetch the Hillstrom MineThatData CSV reproducibly, without depending on
`scikit-uplift` at runtime, and record a checksum. Two public copies were checked on 2026-09-23:

| Copy | URL | Transport | Format | sha256 of CSV bytes |
|---|---|---|---|---|
| Original (Kevin Hillstrom) | `http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv` | HTTP only | CSV, CRLF, 3,964,977 bytes | `0e5893…aece` |
| sklift mirror (S3) | `https://hillstorm1.s3.us-east-2.amazonaws.com/hillstorm_no_indices.csv.gz` | HTTPS | gzip; CSV LF, 4,028,958 bytes | `00a6a8…a2c0` (after gunzip) |

Both parse to the same 64,000 × 12 table with identical columns, dtypes and values (numeric
columns equal within float tolerance). They differ only in formatting (line endings, number
formatting), so their byte hashes differ.

## Options considered
1. **Original as primary, mirror as fallback, one pinned sha256 per source:** canonical
   provenance; HTTP integrity covered by the pinned hash; survives the original site going down /
   two hashes to maintain.
2. Mirror only: HTTPS and smaller / third-party bucket, not the author's copy.
3. `sklift.datasets.fetch_hillstrom()` at runtime: one line / couples the pipeline to a library
   and its cache, and it uses the same mirror anyway.

## Decision
Option 1. Sources are tried in order; a download is accepted only if the sha256 of the (gunzipped)
bytes matches the pin for that source. The raw bytes are stored unchanged as
`data/raw/hillstrom.csv`, and `data/raw/MANIFEST.json` records which source was used, its URL,
`retrieved_at` (UTC), sha256, byte size, row count, columns and any failed sources.

## Consequences
- A tampered or changed file fails loudly instead of flowing into the analysis.
- The silver layer (`xpa clean`) must not depend on formatting, since either copy can land in
  bronze; it parses values, not bytes.
- If either copy changes upstream, the pin must be updated in a new commit that explains why.
- License: publicly released for the 2008 MineThatData challenge; cite Kevin Hillstrom /
  MineThatData. The raw file is not redistributed in this repo.
