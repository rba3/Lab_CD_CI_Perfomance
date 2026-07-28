## 🔮 Predicciones

⚠️ **Tendencia de degradación detectada** (LOW risk)
- Pendiente: +1.03ms/corrida
- P95 actual: 17.0ms
- Días hasta WARN: ~763
- Días hasta FAIL: ~1446
- Confianza: 80%

## 💡 Recomendaciones Prioritarias

🔴 **Tasa de error global crítica**
   - Posibles causas: Problema sistémico (BD caída, network desconectada), PokeAPI inestable
   - Acciones: Revisar estado de PokeAPI (status.pokeapi.co), Revisar logs de la corrida


<!-- JSON Analysis -->
{
  "predictions": {
    "prediction": "DEGRADATION_TREND",
    "confidence": 80,
    "slope_ms_per_run": 1.03,
    "current_p95": 17.0,
    "days_to_warn": 763,
    "days_to_fail": 1446,
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
    "issue": null,
    "root_cause": null,
    "confidence": 0,
    "evidence": []
  },
  "timestamp": "2026-07-28T23:55:30.578321"
}
