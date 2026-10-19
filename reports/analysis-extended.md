## 🔮 Predicciones

⚠️ **Tendencia de degradación detectada** (LOW risk)
- Pendiente: +0.5ms/corrida
- P95 actual: 122.0ms
- Días hasta WARN: ~1356
- Días hasta FAIL: ~2756
- Confianza: 80%

## 🎯 Causa Raíz Identificada

**Latencia inconsistente (outliers)**
- Causa probable: Spikes de latencia, posible GC o context switching
- Confianza: 75%
- Evidencia:
  - p50 (26.0ms) mucho menor que p95 (122.0ms)
  - Diferencia de 3x+ indica distribución anómala


<!-- JSON Analysis -->
{
  "predictions": {
    "prediction": "DEGRADATION_TREND",
    "confidence": 80,
    "slope_ms_per_run": 0.5,
    "current_p95": 122.0,
    "days_to_warn": 1356,
    "days_to_fail": 2756,
    "risk_level": "LOW"
  },
  "recommendations": [],
  "correlations": {},
  "root_cause": {
    "issue": "Latencia inconsistente (outliers)",
    "root_cause": "Spikes de latencia, posible GC o context switching",
    "confidence": 75,
    "evidence": [
      "p50 (26.0ms) mucho menor que p95 (122.0ms)",
      "Diferencia de 3x+ indica distribuci\u00f3n an\u00f3mala"
    ]
  },
  "timestamp": "2026-10-19T18:54:21.754008"
}
