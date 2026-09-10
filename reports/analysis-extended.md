## 🔮 Predicciones

⚠️ **Tendencia de degradación detectada** (MEDIUM risk)
- Pendiente: +39.75ms/corrida
- P95 actual: 97.0ms
- Días hasta WARN: ~17
- Días hasta FAIL: ~35
- Confianza: 80%

## 🎯 Causa Raíz Identificada

**Latencia inconsistente (outliers)**
- Causa probable: Spikes de latencia, posible GC o context switching
- Confianza: 75%
- Evidencia:
  - p50 (27.0ms) mucho menor que p95 (97.0ms)
  - Diferencia de 3x+ indica distribución anómala


<!-- JSON Analysis -->
{
  "predictions": {
    "prediction": "DEGRADATION_TREND",
    "confidence": 80,
    "slope_ms_per_run": 39.75,
    "current_p95": 97.0,
    "days_to_warn": 17,
    "days_to_fail": 35,
    "risk_level": "MEDIUM"
  },
  "recommendations": [],
  "correlations": {},
  "root_cause": {
    "issue": "Latencia inconsistente (outliers)",
    "root_cause": "Spikes de latencia, posible GC o context switching",
    "confidence": 75,
    "evidence": [
      "p50 (27.0ms) mucho menor que p95 (97.0ms)",
      "Diferencia de 3x+ indica distribuci\u00f3n an\u00f3mala"
    ]
  },
  "timestamp": "2026-09-10T16:45:30.195273"
}
