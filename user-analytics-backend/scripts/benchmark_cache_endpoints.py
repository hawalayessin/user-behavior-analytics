from __future__ import annotations

import json
import time
import urllib.error
import urllib.request

BASE_URL = "http://localhost:8000"
TIMEOUT_SECONDS = 90

ENDPOINTS = [
    "/analytics/overview",
    "/analytics/trial/kpis",
    "/analytics/user-activity",
    "/analytics/cross-service/overview",
    "/analytics/cross-service/co-subscriptions",
    "/analytics/cross-service/migrations",
    "/analytics/cross-service/distribution",
    "/analytics/retention/kpis",
    "/analytics/retention/heatmap",
    "/analytics/retention/curve",
    "/analytics/retention/cohorts-list?page=1&page_size=10",
]


def call_once(url: str) -> tuple[float | None, int | None, str | None]:
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as response:
            _ = response.read()
            elapsed_ms = (time.perf_counter() - start) * 1000
            return elapsed_ms, int(response.status), None
    except urllib.error.HTTPError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return elapsed_ms, int(exc.code), f"HTTPError: {exc.reason}"
    except Exception as exc:  # pragma: no cover - runtime diagnostic path
        elapsed_ms = (time.perf_counter() - start) * 1000
        return elapsed_ms, None, str(exc)


def main() -> None:
    print("Cache benchmark: first call vs second call")
    print(f"Base URL: {BASE_URL}")
    print("-")

    rows: list[dict] = []

    for endpoint in ENDPOINTS:
        url = f"{BASE_URL}{endpoint}"

        t1, s1, e1 = call_once(url)
        t2, s2, e2 = call_once(url)

        improvement_pct = None
        if t1 and t2 and t1 > 0:
            improvement_pct = ((t1 - t2) / t1) * 100.0

        row = {
            "endpoint": endpoint,
            "first_ms": round(t1, 2) if t1 is not None else None,
            "second_ms": round(t2, 2) if t2 is not None else None,
            "status_1": s1,
            "status_2": s2,
            "improvement_pct": round(improvement_pct, 2) if improvement_pct is not None else None,
            "error_1": e1,
            "error_2": e2,
        }
        rows.append(row)

        print(json.dumps(row, ensure_ascii=True))

    print("-")
    successful = [r for r in rows if r["status_1"] == 200 and r["status_2"] == 200]
    improved = [r for r in successful if r["improvement_pct"] is not None and r["improvement_pct"] > 0]
    print(
        json.dumps(
            {
                "total": len(rows),
                "successful": len(successful),
                "improved": len(improved),
            },
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
