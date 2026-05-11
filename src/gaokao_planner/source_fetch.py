from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import csv
import ssl


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


@dataclass
class FetchResult:
    source_id: str
    url: str
    status: str
    output_path: str
    bytes_written: int
    error_message: str
    fetched_at: str


def read_source_list(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def ensure_parent(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def detect_antibot_shell(content: bytes) -> bool:
    text = content.decode("utf-8", errors="ignore")
    markers = [
        "window['$_ts']",
        "document.createElement(\"section\")",
        "<body>\n</body>",
    ]
    return all(marker in text for marker in markers[:2]) or markers[2] in text


def fetch_url(url: str, timeout: int = 20, verify_ssl: bool = True) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    context = None
    if not verify_ssl:
        context = ssl._create_unverified_context()
    with urlopen(request, timeout=timeout, context=context) as response:
        return response.read()


def fetch_source(
    source: dict[str, str],
    output_dir: str | Path,
    timeout: int = 20,
) -> FetchResult:
    source_id = source["source_id"]
    url = source["primary_url"]
    year = source.get("year", "") or "unknown"
    output_path = Path(output_dir) / year / f"{source_id}.html"
    fetched_at = datetime.now(timezone.utc).isoformat()

    ensure_parent(output_path)

    try:
        content = fetch_url(url, timeout=timeout, verify_ssl=True)
        if detect_antibot_shell(content):
            output_path.write_bytes(content)
            return FetchResult(
                source_id=source_id,
                url=url,
                status="blocked_antibot_html",
                output_path=str(output_path),
                bytes_written=len(content),
                error_message="Downloaded anti-bot shell instead of source content.",
                fetched_at=fetched_at,
            )
        output_path.write_bytes(content)
        return FetchResult(
            source_id=source_id,
            url=url,
            status="ok",
            output_path=str(output_path),
            bytes_written=len(content),
            error_message="",
            fetched_at=fetched_at,
        )
    except HTTPError as error:
        return FetchResult(
            source_id=source_id,
            url=url,
            status="http_error",
            output_path=str(output_path),
            bytes_written=0,
            error_message=f"{error.code} {error.reason}",
            fetched_at=fetched_at,
        )
    except URLError as error:
        return FetchResult(
            source_id=source_id,
            url=url,
            status="url_error",
            output_path=str(output_path),
            bytes_written=0,
            error_message=str(error.reason),
            fetched_at=fetched_at,
        )
    except ssl.SSLError as error:
        return FetchResult(
            source_id=source_id,
            url=url,
            status="ssl_error",
            output_path=str(output_path),
            bytes_written=0,
            error_message=str(error),
            fetched_at=fetched_at,
        )
    except TimeoutError as error:
        return FetchResult(
            source_id=source_id,
            url=url,
            status="timeout",
            output_path=str(output_path),
            bytes_written=0,
            error_message=str(error),
            fetched_at=fetched_at,
        )
    except Exception as error:  # pragma: no cover - coarse but practical CLI guard.
        return FetchResult(
            source_id=source_id,
            url=url,
            status="error",
            output_path=str(output_path),
            bytes_written=0,
            error_message=str(error),
            fetched_at=fetched_at,
        )


def write_fetch_log(results: Iterable[FetchResult], path: str | Path) -> None:
    output_path = Path(path)
    ensure_parent(output_path)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "source_id",
                "url",
                "status",
                "output_path",
                "bytes_written",
                "error_message",
                "fetched_at",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(result.__dict__)
