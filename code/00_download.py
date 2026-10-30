#!/usr/bin/env python3
"""Download TCIA NSCLC-Radiomics (Lung1) v4 with the NBIA REST API.

Usage:
    python3 code/00_download.py
    python3 code/00_download.py --full --resume --retry 3
    python3 code/00_download.py --full --resume --retry 3 \
        --out ~/tcia/full --log-dir ~/tcia/logs
    python3 code/00_download.py --full --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import ssl
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

API = "https://services.cancerimagingarchive.net/nbia-api/services/v1"
COLLECTION = "NSCLC-Radiomics"
SMALL_PATIENT = "LUNG1-001"

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = REPO_ROOT / "data" / "raw"
DONE_DIR = REPO_ROOT / "logs" / "done"
FAILED_FILE = REPO_ROOT / "logs" / "download_failed.txt"

SKIP_NAMES = {"LICENSE", "metadata.csv", ".DS_Store", ".series.zip"}


def make_ssl_context() -> ssl.SSLContext:
    try:
        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        pass

    for cafile in (
        "/etc/ssl/certs/ca-certificates.crt",
        "/etc/ssl/cert.pem",
        "/etc/pki/tls/certs/ca-bundle.crt",
    ):
        if Path(cafile).exists():
            return ssl.create_default_context(cafile=cafile)

    return ssl.create_default_context()


SSL_CONTEXT = make_ssl_context()


def request(url: str, timeout: int) -> urllib.request.addinfourl:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "tcia-download/1.0"},
    )
    return urllib.request.urlopen(req, timeout=timeout, context=SSL_CONTEXT)


def get_json(url: str, retry: int, timeout: int):
    last_error = None
    for attempt in range(1, retry + 1):
        try:
            with request(url, timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
            if attempt == retry:
                break
            time.sleep(min(2 ** attempt, 30))
    raise RuntimeError(f"getSeries failed: {last_error}")


def list_series(patient: str | None, retry: int, timeout: int) -> list[dict]:
    params = {"Collection": COLLECTION}
    if patient:
        params["PatientID"] = patient
    url = f"{API}/getSeries?{urllib.parse.urlencode(params)}"
    rows = get_json(url, retry, timeout)
    if not isinstance(rows, list):
        raise RuntimeError(f"unexpected getSeries response: {rows!r}")
    return rows


def payload_files(dest: Path) -> list[Path]:
    if not dest.exists():
        return []
    return [
        p
        for p in dest.rglob("*")
        if p.is_file() and p.name not in SKIP_NAMES
    ]


def is_complete(dest: Path, marker: Path, uid: str, expected: int) -> bool:
    if not marker.exists():
        return False
    try:
        meta = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if meta.get("series_uid") != uid:
        return False
    recorded = meta.get("image_count")
    if not isinstance(recorded, int) or recorded < 1:
        return False
    actual = len(payload_files(dest))
    if actual != recorded:
        return False
    if expected and actual != expected:
        return False
    return True


def download_one(
    row: dict,
    out_dir: Path,
    retry: int,
    timeout: int,
    resume: bool,
) -> tuple[str, str, str, str]:
    uid = row["SeriesInstanceUID"]
    patient = row.get("PatientID", "UNKNOWN")
    modality = row.get("Modality", "NA")
    expected = int(row.get("ImageCount") or 0)

    dest = out_dir / patient / modality / uid
    marker = DONE_DIR / uid

    if resume and is_complete(dest, marker, uid, expected):
        return ("skip", patient, modality, uid)

    last_error = ""
    for attempt in range(1, retry + 1):
        tmp = dest / ".series.zip"
        try:
            dest.mkdir(parents=True, exist_ok=True)
            tmp.unlink(missing_ok=True)

            url = f"{API}/getImage?SeriesInstanceUID={urllib.parse.quote(uid)}"
            with request(url, timeout) as resp, open(tmp, "wb") as fh:
                shutil.copyfileobj(resp, fh, length=1024 * 1024)

            with zipfile.ZipFile(tmp) as zf:
                zf.extractall(dest)
            tmp.unlink(missing_ok=True)

            count = len(payload_files(dest))
            if expected and count != expected:
                raise RuntimeError(f"file count {count} != ImageCount {expected}")

            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text(
                json.dumps(
                    {
                        "patient": patient,
                        "modality": modality,
                        "series_uid": uid,
                        "image_count": count,
                    },
                    ensure_ascii=False,
                )
                + "\n",
                encoding="utf-8",
            )
            return ("ok", patient, modality, uid)
        except Exception as exc:
            tmp.unlink(missing_ok=True)
            last_error = str(exc)
            if attempt == retry:
                break
            time.sleep(min(2 ** attempt, 30))

    return ("fail", patient, modality, f"{uid}\t{last_error}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download NSCLC-Radiomics (Lung1) v4 via TCIA REST API."
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="download the whole collection; default is LUNG1-001 only",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="skip series already marked complete",
    )
    parser.add_argument(
        "--retry",
        type=int,
        default=3,
        help="retries per series (default: 3)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        help="parallel series downloads (default: 8)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=600,
        help="socket timeout in seconds (default: 600)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="only process the first N series; 0 means all (testing aid)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="output directory (default: data/raw under the repo root)",
    )
    parser.add_argument(
        "--log-dir",
        default=None,
        help="log/state directory (default: logs under the repo root)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="list series without downloading",
    )
    args = parser.parse_args()
    if args.retry < 1:
        parser.error("--retry must be >= 1")
    if args.workers < 1:
        parser.error("--workers must be >= 1")
    if args.timeout < 1:
        parser.error("--timeout must be >= 1")
    if args.limit < 0:
        parser.error("--limit must be >= 0")
    return args


def main() -> int:
    global DONE_DIR, FAILED_FILE

    args = parse_args()
    patient = None if args.full else SMALL_PATIENT
    out_dir = Path(args.out).expanduser() if args.out else DEFAULT_OUT
    log_dir = Path(args.log_dir).expanduser() if args.log_dir else REPO_ROOT / "logs"
    DONE_DIR = log_dir / "done"
    FAILED_FILE = log_dir / "download_failed.txt"

    try:
        rows = list_series(patient, args.retry, args.timeout)
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.limit:
        rows = rows[: args.limit]

    print(f"series: {len(rows)}")
    print(f"output: {out_dir}")
    if args.dry_run:
        for row in rows[:5]:
            print(
                row.get("PatientID"),
                row.get("Modality"),
                row.get("ImageCount"),
                row.get("SeriesInstanceUID"),
            )
        if len(rows) > 5:
            print(f"... {len(rows) - 5} more")
        return 0

    ok = 0
    skip = 0
    failed: list[str] = []

    executor = ThreadPoolExecutor(max_workers=args.workers)
    try:
        futures = [
            executor.submit(
                download_one,
                row,
                out_dir,
                args.retry,
                args.timeout,
                args.resume,
            )
            for row in rows
        ]
        for future in as_completed(futures):
            status, patient_id, modality, detail = future.result()
            if status == "ok":
                ok += 1
                print(f"[ok] {patient_id} {modality} {detail}", flush=True)
            elif status == "skip":
                skip += 1
                print(f"[skip] {patient_id} {modality} {detail}", flush=True)
            else:
                failed.append(f"{patient_id}\t{modality}\t{detail}")
                print(f"[fail] {patient_id} {modality} {detail}", file=sys.stderr, flush=True)
    except KeyboardInterrupt:
        print("\ninterrupted; completed series are kept", file=sys.stderr)
        executor.shutdown(wait=False, cancel_futures=True)
        os._exit(130)
    finally:
        executor.shutdown(wait=False, cancel_futures=True)

    FAILED_FILE.parent.mkdir(parents=True, exist_ok=True)
    if failed:
        FAILED_FILE.write_text("\n".join(failed) + "\n", encoding="utf-8")
        print(f"failed list: {FAILED_FILE}")
    else:
        FAILED_FILE.unlink(missing_ok=True)

    print(f"ok={ok} skip={skip} fail={len(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
