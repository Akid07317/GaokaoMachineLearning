from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl
from urllib.request import Request, urlopen

import csv
import ssl

from gaokao_planner.source_fetch import build_headers, detect_antibot_shell, ensure_parent


@dataclass
class ApiFetchResult:
    source_id: str
    source_name: str
    segment: str
    target_kind: str
    url: str
    method: str
    request_body: str
    status: str
    output_path: str
    bytes_written: int
    error_message: str
    fetched_at: str


def read_target_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def _encode_body(request_body: str) -> bytes | None:
    if not request_body:
        return None
    normalized = "&".join(f"{key}={value}" for key, value in parse_qsl(request_body, keep_blank_values=True))
    return normalized.encode("utf-8")


def fetch_request(
    url: str,
    *,
    method: str = "GET",
    request_body: str = "",
    timeout: int = 20,
    verify_ssl: bool = True,
    extra_headers: dict[str, str] | None = None,
) -> bytes:
    headers = build_headers(extra_headers=extra_headers)
    data = _encode_body(request_body)
    if method.upper() == "POST":
        headers.setdefault("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
    request = Request(url, data=data, headers=headers, method=method.upper())
    context = None
    if not verify_ssl:
        context = ssl._create_unverified_context()
    with urlopen(request, timeout=timeout, context=context) as response:
        return response.read()


def fetch_api_target(
    row: dict[str, str],
    *,
    output_dir: str | Path,
    timeout: int = 20,
    verify_ssl: bool = True,
) -> ApiFetchResult:
    source_id = row.get("source_id", "unknown")
    source_name = row.get("source_name", "")
    segment = row.get("segment", "")
    target_kind = row.get("target_kind", "api")
    url = row.get("url", "")
    method = (row.get("method", "GET") or "GET").upper()
    request_body = row.get("request_body", "")
    slug = row.get("target_slug", "") or "target"
    suffix = row.get("file_suffix", ".json") or ".json"
    output_path = Path(output_dir) / source_id / f"{slug}{suffix}"
    fetched_at = datetime.now(timezone.utc).isoformat()

    ensure_parent(output_path)

    try:
        content = fetch_request(
            url,
            method=method,
            request_body=request_body,
            timeout=timeout,
            verify_ssl=verify_ssl,
        )
        output_path.write_bytes(content)
        status = "blocked_antibot_html" if detect_antibot_shell(content) else "ok"
        message = ""
        if status != "ok":
            message = "Downloaded anti-bot shell instead of API payload."
        return ApiFetchResult(
            source_id=source_id,
            source_name=source_name,
            segment=segment,
            target_kind=target_kind,
            url=url,
            method=method,
            request_body=request_body,
            status=status,
            output_path=str(output_path),
            bytes_written=len(content),
            error_message=message,
            fetched_at=fetched_at,
        )
    except HTTPError as error:
        return ApiFetchResult(
            source_id=source_id,
            source_name=source_name,
            segment=segment,
            target_kind=target_kind,
            url=url,
            method=method,
            request_body=request_body,
            status="http_error",
            output_path=str(output_path),
            bytes_written=0,
            error_message=f"{error.code} {error.reason}",
            fetched_at=fetched_at,
        )
    except URLError as error:
        return ApiFetchResult(
            source_id=source_id,
            source_name=source_name,
            segment=segment,
            target_kind=target_kind,
            url=url,
            method=method,
            request_body=request_body,
            status="url_error",
            output_path=str(output_path),
            bytes_written=0,
            error_message=str(error.reason),
            fetched_at=fetched_at,
        )
    except ssl.SSLError as error:
        return ApiFetchResult(
            source_id=source_id,
            source_name=source_name,
            segment=segment,
            target_kind=target_kind,
            url=url,
            method=method,
            request_body=request_body,
            status="ssl_error",
            output_path=str(output_path),
            bytes_written=0,
            error_message=str(error),
            fetched_at=fetched_at,
        )
    except TimeoutError as error:
        return ApiFetchResult(
            source_id=source_id,
            source_name=source_name,
            segment=segment,
            target_kind=target_kind,
            url=url,
            method=method,
            request_body=request_body,
            status="timeout",
            output_path=str(output_path),
            bytes_written=0,
            error_message=str(error),
            fetched_at=fetched_at,
        )
    except Exception as error:  # pragma: no cover - CLI guard for mixed vendor sites.
        return ApiFetchResult(
            source_id=source_id,
            source_name=source_name,
            segment=segment,
            target_kind=target_kind,
            url=url,
            method=method,
            request_body=request_body,
            status="error",
            output_path=str(output_path),
            bytes_written=0,
            error_message=str(error),
            fetched_at=fetched_at,
        )


def write_api_fetch_log(results: Iterable[ApiFetchResult], path: str | Path) -> None:
    output_path = Path(path)
    ensure_parent(output_path)
    fieldnames = [
        "source_id",
        "source_name",
        "segment",
        "target_kind",
        "url",
        "method",
        "request_body",
        "status",
        "output_path",
        "bytes_written",
        "error_message",
        "fetched_at",
    ]
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for result in results:
            writer.writerow(result.__dict__)
