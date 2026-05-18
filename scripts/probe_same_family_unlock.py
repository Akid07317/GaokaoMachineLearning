from __future__ import annotations

import argparse
import csv
import json
import ssl
from dataclasses import dataclass
from datetime import datetime, timezone
from http.cookiejar import CookieJar
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlparse
from urllib.request import HTTPCookieProcessor, HTTPSHandler, Request, build_opener


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


@dataclass
class ProbeResult:
    school_key: str
    probe_kind: str
    url: str
    method: str
    request_body: str
    status: str
    http_code: str
    bytes_written: int
    output_path: str
    error_message: str
    fetched_at: str


SCHOOLS = [
    {
        "school_key": "hefei_gongda_211",
        "plan_page": "http://bkzs.hfut.edu.cn/static/front/hfut/basic/html_web/zsjh.html",
        "score_page": "http://bkzs.hfut.edu.cn/static/front/hfut/basic/html_web/lnfs.html",
    },
    {
        "school_key": "haerbin_gongcheng_211",
        "plan_page": "https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/zsjh.html",
        "score_page": "https://zsb.hrbeu.edu.cn/static/front/hrbeu/basic/html_web/lnfs.html",
    },
    {
        "school_key": "dalian_haishi_211",
        "plan_page": "https://sjcx.dlmu.edu.cn/static/front/dlmu/basic/html_web/zsjh.html",
        "score_page": "https://sjcx.dlmu.edu.cn/static/front/dlmu/basic/html_web/lnfs.html",
    },
]


def html_headers() -> dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }


def ajax_headers(referer: str) -> dict[str, str]:
    parsed = urlparse(referer)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    return {
        "User-Agent": USER_AGENT,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Origin": origin,
        "Referer": referer,
        "X-Requested-With": "XMLHttpRequest",
    }


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def request_with_opener(
    opener,
    url: str,
    *,
    method: str = "GET",
    request_body: str = "",
    headers: dict[str, str] | None = None,
    timeout: int = 25,
):
    data = request_body.encode("utf-8") if request_body else None
    req = Request(url, data=data, headers=headers or {}, method=method.upper())
    with opener.open(req, timeout=timeout) as response:
        return response.read(), str(getattr(response, "status", "")) or "200"


def run_probe(
    school: dict[str, str],
    *,
    output_dir: Path,
    timeout: int,
    verify_ssl: bool,
) -> list[ProbeResult]:
    cookie_jar = CookieJar()
    handlers = [HTTPCookieProcessor(cookie_jar)]
    if not verify_ssl:
        handlers.append(HTTPSHandler(context=ssl._create_unverified_context()))
    opener = build_opener(*handlers)
    results: list[ProbeResult] = []
    school_dir = output_dir / school["school_key"]
    ensure_parent(school_dir / "placeholder")

    def record(
        probe_kind: str,
        url: str,
        method: str,
        request_body: str,
        status: str,
        http_code: str,
        payload: bytes,
        error_message: str,
    ) -> None:
        slug = probe_kind
        out_path = school_dir / f"{slug}.bin"
        if payload:
            out_path.write_bytes(payload)
        results.append(
            ProbeResult(
                school_key=school["school_key"],
                probe_kind=probe_kind,
                url=url,
                method=method,
                request_body=request_body,
                status=status,
                http_code=http_code,
                bytes_written=len(payload),
                output_path=str(out_path) if payload else "",
                error_message=error_message,
                fetched_at=datetime.now(timezone.utc).isoformat(),
            )
        )

    pages = [
        ("plan_page_get", school["plan_page"], "GET", "", html_headers()),
        ("score_page_get", school["score_page"], "GET", "", html_headers()),
        (
            "plan_param",
            school["plan_page"].split("/static/front/")[0] + "/f/ajax_zsjh_param",
            "POST",
            "",
            ajax_headers(school["plan_page"]),
        ),
        (
            "score_param",
            school["score_page"].split("/static/front/")[0] + "/f/ajax_lnfs_param",
            "POST",
            "",
            ajax_headers(school["score_page"]),
        ),
    ]
    for year, klmc, kl_slug in [("2025", "物理类", "physics"), ("2025", "理工", "science")]:
        body = urlencode({"ssmc": "广西", "zsnf": year, "klmc": klmc, "zslx": "普通类"})
        pages.extend(
            [
                (
                    f"plan_probe_{year}_{kl_slug}",
                    school["plan_page"].split("/static/front/")[0] + "/f/ajax_zsjh",
                    "POST",
                    body,
                    ajax_headers(school["plan_page"]),
                ),
                (
                    f"score_probe_{year}_{kl_slug}",
                    school["score_page"].split("/static/front/")[0] + "/f/ajax_lnfs",
                    "POST",
                    body,
                    ajax_headers(school["score_page"]),
                ),
            ]
        )

    for probe_kind, url, method, request_body, headers in pages:
        try:
            payload, code = request_with_opener(
                opener,
                url,
                method=method,
                request_body=request_body,
                headers=headers,
                timeout=timeout,
            )
            record(probe_kind, url, method, request_body, "ok", code, payload, "")
        except HTTPError as error:
            record(probe_kind, url, method, request_body, "http_error", str(error.code), b"", f"{error.code} {error.reason}")
        except URLError as error:
            record(probe_kind, url, method, request_body, "url_error", "", b"", str(error.reason))
        except ssl.SSLError as error:
            record(probe_kind, url, method, request_body, "ssl_error", "", b"", str(error))
        except TimeoutError as error:
            record(probe_kind, url, method, request_body, "timeout", "", b"", str(error))
        except Exception as error:  # pragma: no cover
            record(probe_kind, url, method, request_body, "error", "", b"", str(error))
    return results


def write_results(rows: list[ProbeResult], output_path: Path) -> None:
    ensure_parent(output_path)
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "school_key",
                "probe_kind",
                "url",
                "method",
                "request_body",
                "status",
                "http_code",
                "bytes_written",
                "output_path",
                "error_message",
                "fetched_at",
            ],
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row.__dict__)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Probe same-family admissions AJAX endpoints with browser-like headers."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("raw_data") / "engineering_same_family_probe",
        help="Directory for raw probe payloads.",
    )
    parser.add_argument(
        "--log-path",
        type=Path,
        default=Path("reports") / "engineering_same_family_probe.csv",
        help="CSV log path.",
    )
    parser.add_argument("--timeout", type=int, default=25)
    parser.add_argument("--insecure", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    all_rows: list[ProbeResult] = []
    for school in SCHOOLS:
        all_rows.extend(
            run_probe(
                school,
                output_dir=args.output_dir,
                timeout=args.timeout,
                verify_ssl=not args.insecure,
            )
        )
    write_results(all_rows, args.log_path)
    ok_count = sum(1 for row in all_rows if row.status == "ok")
    print(f"Wrote {len(all_rows)} probe rows with {ok_count} ok to {args.log_path}.")


if __name__ == "__main__":
    main()
