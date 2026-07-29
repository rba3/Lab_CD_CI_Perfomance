## 🔮 Predicciones

⚠️ **Tendencia de degradación detectada** (LOW risk)
- Pendiente: +0.15ms/corrida
- P95 actual: 694.3ms
- Días hasta WARN: ~704
- Días hasta FAIL: ~5371
- Confianza: 80%

## 🎯 Causa Raíz Identificada

**Latencia inconsistente (outliers)**
- Causa probable: Spikes de latencia, posible GC o context switching
- Confianza: 75%
- Evidencia:
  - p50 (111.0ms) mucho menor que p95 (694.3ms)
  - Diferencia de 3x+ indica distribución anómala


<!-- JSON Analysis -->
{
  "predictions": {
    "prediction": "DEGRADATION_TREND",
    "confidence": 80,
    "slope_ms_per_run": 0.15,
    "current_p95": 694.3,
    "days_to_warn": 704,
    "days_to_fail": 5371,
    "risk_level": "LOW"
  },
  "recommendations": [],
  "correlations": {},
  "root_cause": {
    "issue": "Latencia inconsistente (outliers)",
    "root_cause": "Spikes de latencia, posible GC o context switching",
    "confidence": 75,
    "evidence": [
      "p50 (111.0ms) mucho menor que p95 (694.3ms)",
      "Diferencia de 3x+ indica distribuci\u00f3n an\u00f3mala"
    ]
  },
  "timestamp": "2026-07-29T00:38:08.634693"
}
