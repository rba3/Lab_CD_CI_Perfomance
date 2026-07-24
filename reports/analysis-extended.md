## 🔮 Predicciones

✓ STABLE

## 💡 Recomendaciones Prioritarias

🔴 **Latencia crítica (p95 > 1500ms)**
   - Posibles causas: Ver análisis de endpoints específicos
   - Acciones: Revisar recomendaciones por endpoint arriba

## 🎯 Causa Raíz Identificada

**Latencia inconsistente (outliers)**
- Causa probable: Spikes de latencia, posible GC o context switching
- Confianza: 75%
- Evidencia:
  - p50 (245.5ms) mucho menor que p95 (2901.8ms)
  - Diferencia de 3x+ indica distribución anómala


<!-- JSON Analysis -->
{
  "predictions": {
    "prediction": "STABLE",
    "confidence": 0,
    "slope_ms_per_run": -6.0,
    "current_p95": 2901.8,
    "days_to_warn": null,
    "days_to_fail": null,
    "risk_level": "LOW"
  },
  "recommendations": [
    {
      "issue": "Latencia cr\u00edtica (p95 > 1500ms)",
      "severity": "CRITICAL",
      "causes": [
        "Ver an\u00e1lisis de endpoints espec\u00edficos"
      ],
      "fixes": [
        "Revisar recomendaciones por endpoint arriba"
      ]
    }
  ],
  "correlations": {},
  "root_cause": {
    "issue": "Latencia inconsistente (outliers)",
    "root_cause": "Spikes de latencia, posible GC o context switching",
    "confidence": 75,
    "evidence": [
      "p50 (245.5ms) mucho menor que p95 (2901.8ms)",
      "Diferencia de 3x+ indica distribuci\u00f3n an\u00f3mala"
    ]
  },
  "timestamp": "2026-07-24T18:43:34.157965"
}
