#!/usr/bin/env python3
"""Convierte un JTL de JMeter en metricas agregadas (JSON).

Uso:
    python scripts/parse_results.py <archivo.jtl> <escenario> <salida.json>

El JTL debe estar en formato CSV (default de JMeter con -l).
"""
import csv
import json
import sys
from statistics import mean


def percentile(values, pct):
    """Percentil por interpolacion lineal (misma logica que JMeter)."""
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    rank = (pct / 100.0) * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    frac = rank - low
    return round(ordered[low] + (ordered[high] - ordered[low]) * frac, 1)


def summarize(rows):
    elapsed = [r["elapsed"] for r in rows]
    errors = sum(1 for r in rows if not r["success"])
    total = len(rows)
    ts_start = min(r["ts"] for r in rows)
    ts_end = max(r["ts"] + r["elapsed"] for r in rows)
    duration_s = max((ts_end - ts_start) / 1000.0, 0.001)
    return {
        "samples": total,
        "errors": errors,
        "error_pct": round(errors / total * 100, 2) if total else 0.0,
        "avg_ms": round(mean(elapsed), 1) if elapsed else 0.0,
        "min_ms": min(elapsed) if elapsed else 0,
        "max_ms": max(elapsed) if elapsed else 0,
        "p50_ms": percentile(elapsed, 50),
        "p90_ms": percentile(elapsed, 90),
        "p95_ms": percentile(elapsed, 95),
        "p99_ms": percentile(elapsed, 99),
        "throughput_rps": round(total / duration_s, 2),
        "duration_s": round(duration_s, 1),
    }


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    jtl_path, scenario, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

    rows = []
    with open(jtl_path, newline="", encoding="utf-8", errors="replace") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            try:
                rows.append({
                    "ts": int(r["timeStamp"]),
                    "elapsed": int(r["elapsed"]),
                    "label": r.get("label", "unknown"),
                    "code": r.get("responseCode", ""),
                    "success": str(r.get("success", "")).strip().lower() == "true",
                })
            except (ValueError, KeyError):
                continue

    if not rows:
        print(f"AVISO: no se encontraron muestras en {jtl_path}")
        result = {"scenario": scenario, "overall": {}, "by_endpoint": {}, "empty": True}
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, ensure_ascii=False)
        return

    by_label = {}
    for r in rows:
        by_label.setdefault(r["label"], []).append(r)

    result = {
        "scenario": scenario,
        "overall": summarize(rows),
        "by_endpoint": {label: summarize(rs) for label, rs in sorted(by_label.items())},
        "empty": False,
    }

    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)

    o = result["overall"]
    print(f"[{scenario}] muestras={o['samples']} errores={o['error_pct']}% "
          f"p95={o['p95_ms']}ms throughput={o['throughput_rps']} rps -> {out_path}")


if __name__ == "__main__":
    main()
