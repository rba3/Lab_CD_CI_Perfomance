#!/usr/bin/env python3
"""
Script de ejemplo: Cómo usar ai_analysis.py localmente
Útil para testing y desarrollo
"""

import json
from ai_analysis import AIAnalysisEngine

# Ejemplo 1: Métricas simples sin histórico
print("=" * 70)
print("EJEMPLO 1: Análisis sin histórico")
print("=" * 70)

current_metrics = {
    "overall": {
        "error_pct": 0.5,
        "p50_ms": 150,
        "p95_ms": 450,
        "p99_ms": 650,
        "throughput": 15.5,
        "sample_count": 1000
    },
    "endpoints": {
        "pokemon": {
            "p50_ms": 120,
            "p95_ms": 350,
            "p99_ms": 500,
            "error_pct": 0.0,
            "throughput": 18.2
        },
        "type": {
            "p50_ms": 180,
            "p95_ms": 550,
            "p99_ms": 800,
            "error_pct": 1.2,
            "throughput": 12.8
        }
    }
}

engine = AIAnalysisEngine(current_metrics)
engine.predict_degradation()
engine.generate_recommendations()
engine.analyze_correlations()
engine.identify_root_cause()

print(engine.to_markdown())

# Ejemplo 2: Con histórico (simular degradación)
print("\n" + "=" * 70)
print("EJEMPLO 2: Análisis CON histórico (tendencia de degradación)")
print("=" * 70)

# Simular 7 corridas con degradación progresiva
historical = []
for day in range(7):
    p95_value = 300 + (day * 25)  # Sube 25ms/día
    run = {
        "timestamp": f"2026-07-{17+day}",
        "overall": {
            "error_pct": 0.1,
            "p50_ms": 100,
            "p95_ms": p95_value,
            "p99_ms": p95_value + 200,
            "throughput": 20.0,
            "sample_count": 1000
        },
        "endpoints": {
            "pokemon": {
                "p95_ms": p95_value - 50,
                "error_pct": 0.0,
                "throughput": 22.0
            },
            "type": {
                "p95_ms": p95_value + 50,
                "error_pct": 0.2,
                "throughput": 18.0
            }
        }
    }
    historical.append(run)

# Corrida actual con tendencia
current_with_trend = {
    "overall": {
        "error_pct": 0.15,
        "p50_ms": 120,
        "p95_ms": 475,  # Sigue subiendo
        "p99_ms": 700,
        "throughput": 19.0,
        "sample_count": 1000
    },
    "endpoints": {
        "pokemon": {
            "p95_ms": 425,
            "error_pct": 0.0,
            "throughput": 21.0
        },
        "type": {
            "p95_ms": 525,
            "error_pct": 0.3,  # Empeorando
            "throughput": 17.0
        }
    }
}

engine2 = AIAnalysisEngine(current_with_trend, historical)
engine2.predict_degradation()
engine2.generate_recommendations()
engine2.analyze_correlations()
engine2.identify_root_cause()

print(engine2.to_markdown())

# Ejemplo 3: Exportar como JSON
print("\n" + "=" * 70)
print("EJEMPLO 3: Exportar análisis como JSON (para máquinas)")
print("=" * 70)

analysis_dict = engine2.to_dict()
print(json.dumps(analysis_dict, indent=2))

print("\n" + "=" * 70)
print("✅ Ejemplos completados")
print("=" * 70)
