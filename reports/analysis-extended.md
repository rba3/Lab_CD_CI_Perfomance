## 🔮 Predicciones

⚠️ **Tendencia de degradación detectada** (MEDIUM risk)
- Pendiente: +34.75ms/corrida
- P95 actual: 156.0ms
- Días hasta WARN: ~18
- Días hasta FAIL: ~38
- Confianza: 80%

## 🎯 Causa Raíz Identificada

**Latencia inconsistente (outliers)**
- Causa probable: Spikes de latencia, posible GC o context switching
- Confianza: 75%
- Evidencia:
  - p50 (25.0ms) mucho menor que p95 (156.0ms)
  - Diferencia de 3x+ indica distribución anómala


<!-- JSON Analysis -->
{
  "predictions": {
    "prediction": "DEGRADATION_TREND",
    "confidence": 80,
    "slope_ms_per_run": 34.75,
    "current_p95": 156.0,
    "days_to_warn": 18,
    "days_to_fail": 38,
    "risk_level": "MEDIUM"
  },
  "recommendations": [],
  "correlations": {},
  "root_cause": {
    "issue": "Latencia inconsistente (outliers)",
    "root_cause": "Spikes de latencia, posible GC o context switching",
    "confidence": 75,
    "evidence": [
      "p50 (25.0ms) mucho menor que p95 (156.0ms)",
      "Diferencia de 3x+ indica distribuci\u00f3n an\u00f3mala"
    ]
  },
  "timestamp": "2026-09-01T17:02:52.273023"
}
