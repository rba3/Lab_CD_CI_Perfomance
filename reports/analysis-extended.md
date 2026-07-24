## 🔮 Predicciones

⚠️ **Tendencia de degradación detectada** (LOW risk)
- Pendiente: +0.63ms/corrida
- P95 actual: 112.8ms
- Días hasta WARN: ~1085
- Días hasta FAIL: ~2190
- Confianza: 60%

## 💡 Recomendaciones Prioritarias

🔴 **Tasa de error global crítica**
   - Posibles causas: Problema sistémico (BD caída, network desconectada), PokeAPI inestable
   - Acciones: Revisar estado de PokeAPI (status.pokeapi.co), Revisar logs de la corrida

## 🎯 Causa Raíz Identificada

**Latencia inconsistente (outliers)**
- Causa probable: Spikes de latencia, posible GC o context switching
- Confianza: 75%
- Evidencia:
  - p50 (9.0ms) mucho menor que p95 (112.8ms)
  - Diferencia de 3x+ indica distribución anómala


<!-- JSON Analysis -->
{
  "predictions": {
    "prediction": "DEGRADATION_TREND",
    "confidence": 60,
    "slope_ms_per_run": 0.63,
    "current_p95": 112.8,
    "days_to_warn": 1085,
    "days_to_fail": 2190,
    "risk_level": "LOW"
  },
  "recommendations": [
    {
      "issue": "Tasa de error global cr\u00edtica",
      "severity": "CRITICAL",
      "causes": [
        "Problema sist\u00e9mico (BD ca\u00edda, network desconectada)",
        "PokeAPI inestable",
        "Assertions muy restrictivas"
      ],
      "fixes": [
        "Revisar estado de PokeAPI (status.pokeapi.co)",
        "Revisar logs de la corrida",
        "Considerar relajar assertions",
        "Abrir issue en PokeAPI si es su problema"
      ]
    }
  ],
  "correlations": {},
  "root_cause": {
    "issue": "Latencia inconsistente (outliers)",
    "root_cause": "Spikes de latencia, posible GC o context switching",
    "confidence": 75,
    "evidence": [
      "p50 (9.0ms) mucho menor que p95 (112.8ms)",
      "Diferencia de 3x+ indica distribuci\u00f3n an\u00f3mala"
    ]
  },
  "timestamp": "2026-07-24T23:53:29.610237"
}
