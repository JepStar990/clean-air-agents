"""
OpenAQ bulk ingestion (daily gzipped CSVs from the public AWS S3 archive).

Registry docs & S3 bucket info: [1](https://huggingface.co/docs/hub/spaces)

Notes:
- For simplicity, we provide a naive "file list" (two recent samples). In production,
  use `aws s3 ls --no-sign-request s3://openaq-data-archive/` to enumerate dates,
  or an index published by OpenAQ (if available).
"""

import gzip
import csv
from typing import List, Dict
import httpx

S3_BUCKET = "https://openaq-data-archive.s3.amazonaws.com/"


async def list_archive(prefix: str = "") -> List[str]:
    # Naive: a small sample — replace with AWS CLI or an API listing in production.
    # Format: YYYY-MM-DD.csv.gz
    return [
        f"{S3_BUCKET}2025-11-01.csv.gz",
        f"{S3_BUCKET}2025-11-02.csv.gz",
    ]


async def download_csv_gz(url: str) -> List[Dict]:
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.get(url)
        r.raise_for_status()
        content = gzip.decompress(r.content).decode("utf-8", errors="replace")
        rows = []
        reader = csv.DictReader(content.splitlines())
        for row in reader:
            rows.append(row)
        return rows
