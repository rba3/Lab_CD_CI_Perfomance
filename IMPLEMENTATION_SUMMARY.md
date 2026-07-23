# 📋 Resumen de Cambios - Análisis Extendido de Performance

## 🎯 Objetivo
Mejorar el laboratorio de performance con análisis avanzado de IA que proporcione:
- Predicciones de degradación
- Recomendaciones automáticas
- Análisis de correlaciones
- Identificación de causa raíz

---

## 📦 Archivos Creados

### 1. `scripts/ai_analysis.py` (18.5 KB)
**Motor de análisis avanzado**

Características:
- ✅ Detecta tendencias en latencia (pendiente p95)
- ✅ Predice cuándo se alcanzarán umbrales WARN/FAIL
- ✅ Genera recomendaciones específicas por endpoint
- ✅ Calcula correlaciones de Pearson entre endpoints
- ✅ Identifica causa raíz probable
- ✅ Exporta a Markdown y JSON

Clase principal: `AIAnalysisEngine`

```python
engine = AIAnalysisEngine(current_metrics, historical_metrics)
engine.predict_degradation()
engine.generate_recommendations()
engine.analyze_correlations()
engine.identify_root_cause()
```

### 2. `scripts/gen_report_enhanced.py` (7.8 KB)
**Generador de reportes mejorado**

Características:
- ✅ Integra análisis de `ai_analysis.py`
- ✅ Genera reporte Markdown completo
- ✅ Incluye gráficos Mermaid de tendencia histórica
- ✅ Métricas globales y por endpoint
- ✅ JSON técnico para análisis posterior

Uso:
```bash
python3 scripts/gen_report_enhanced.py \
  --metrics reports/metrics.json \
  --verdict verdict.md \
  --date "2026-07-24 10:30 UTC" \
  --run-url "https://..." \
  --historical reports/historical.json \
  --out reports/report.md
```

### 3. `scripts/example_ai_analysis.py` (3.0 KB)
**Ejemplos de uso locales**

Demuestra:
- Análisis sin histórico
- Análisis con degradación simulada
- Exportación a JSON

Ejecutar:
```bash
python3 scripts/example_ai_analysis.py
```

### 4. `docs/AI_ANALYSIS.md` (6.7 KB)
**Documentación completa**

Incluye:
- Overview del sistema
- Guía de uso
- Interpretación de resultados
- Troubleshooting
- Ejemplos

---

## 🔄 Archivos Modificados

### `.github/workflows/perf-tests.yml`
**Cambios en el workflow de GitHub Actions**

Nuevos pasos:

1. **Cargar histórico de corridas**
   ```bash
   git show HEAD:reports/historical.json > reports/historical.json
   ```

2. **Análisis extendido con IA**
   ```bash
   python3 scripts/ai_analysis.py \
     reports/metrics-consolidated.json \
     reports/historical.json \
     > reports/analysis-extended.md
   ```

3. **Generar reporte mejorado**
   ```bash
   python3 scripts/gen_report_enhanced.py \
     --metrics reports/metrics-consolidated.json \
     --verdict verdict.md \
     --date "$HUMAN" \
     --run-url "$RUN_URL" \
     --historical reports/historical.json \
     --out "reports/report-${STAMP}.md"
   ```

4. **Actualizar histórico**
   - Agrega corrida actual al histórico
   - Mantiene últimas 30 corridas
   - Guarda en `reports/historical.json`

5. **Issue mejorado**
   - Incluye análisis extendido (predicciones, correlaciones)
   - Más contexto para investigación

---

## 📊 Ejemplo de Salida

### Reporte Mejorado
```
# 📊 Reporte de Performance - PokeAPI

## ✅ Veredicto
PASS - Dentro de SLOs

## 🔮 Predicciones
⚠️ Tendencia de degradación detectada (HIGH risk)
- Pendiente: +0.5ms/corrida
- P95 actual: 475ms
- Días hasta WARN: ~10

## 💡 Recomendaciones Prioritarias
🔴 Tasa de error elevada (1.2%)
   - Endpoint: type
   - Causas: Schema JSON cambió, Timeout
   - Acciones: Revisar PokeAPI, Aumentar timeout

## 🔗 Correlaciones
- pokemon ↔ type (0.95): Muy correlacionados

## 🎯 Causa Raíz
Problema en endpoint específico (type)
- Confianza: 80%
```

---

## 🚀 Cómo Usar

### En GitHub Actions (Automático)
- Cron diario: Ejecuta análisis automáticamente
- Manual: `Actions → Performance PokeAPI → Run workflow`
- Pull Request: Valida performance antes de merge

**Todo ocurre automáticamente en estos pasos del workflow**

### Localmente (Testing)
```bash
# 1. Ver ejemplos
python3 scripts/example_ai_analysis.py

# 2. Con datos reales después de JMeter
python3 scripts/ai_analysis.py \
  reports/metrics-smoke.json \
  reports/historical.json

# 3. Generar reporte completo
python3 scripts/gen_report_enhanced.py \
  --metrics reports/metrics-smoke.json \
  --verdict verdict.md \
  --out reports/test-report.md
```

---

## 📈 Métricas y KPIs

### Predicciones
- **Slope**: Cambio en p95 por corrida (ms/día)
- **Days to WARN**: Estimación de cuándo alcanzará threshold
- **Days to FAIL**: Estimación de cuándo fallará completamente
- **Confidence**: 0-100%, basado en cantidad de datos históricos

### Recomendaciones
- **Severity**: CRITICAL, HIGH, MEDIUM, LOW
- **Por endpoint**: Diagnosticadas individualmente
- **Actionable**: Incluyen causa probable y solución

### Correlaciones
- **Rango**: 0 a 1 (0 = independientes, 1 = idénticas)
- **Umbral significativo**: > 0.7
- **Interpretación**: Indica recursos compartidos

---

## ⚙️ Configuración

### SLOs (en `ai_analysis.py`)
```python
threshold_warn = 800    # p95 en ms para WARN
threshold_fail = 1500   # p95 en ms para FAIL
```

### Histórico (en workflow)
```bash
# Cambiar cantidad de corridas guardadas:
TRIMMED=$(echo "$UPDATED" | jq '.[-30:]')  # Actualmente 30
```

### Sensibilidad de Predicciones (en `ai_analysis.py`)
```python
recent = self.history[-5:]  # Últimas 5 corridas para tendencia
```

---

## 🔍 Diagnóstico

### Si p95 sube pero p50 no (spike de latencia)
→ Outliers/GC pause, indica distribución anómala

### Si todos los endpoints suben juntos
→ Problema sistémico: PokeAPI lenta o red degradada

### Si solo uno/dos endpoints con error
→ Problema específico de ese endpoint

### Si dos endpoints muy correlacionados (>0.95)
→ Comparten infraestructura, afecta a ambos

---

## 📝 Ejemplo de Histórico Guardado

Archivo: `reports/historical.json`
```json
[
  {
    "timestamp": "2026-07-23T10:30:00Z",
    "overall": {
      "error_pct": 0.1,
      "p50_ms": 150,
      "p95_ms": 450,
      "p99_ms": 650,
      "throughput": 15.5
    },
    "endpoints": {
      "pokemon": {"p95_ms": 350, ...},
      "type": {"p95_ms": 550, ...}
    }
  },
  ...últimas 30 corridas...
]
```

---

## ✅ Beneficios

1. **Proactivo**: Detecta problemas ANTES de que causen FAIL
2. **Inteligente**: Entiende correlaciones y causa raíz
3. **Accionable**: Recomendaciones específicas
4. **Histórico**: Mantiene contexto de últimas 30 corridas
5. **Automatizado**: Sin intervención manual
6. **Transparente**: JSON exportable para análisis posterior

---

## 🎓 Próximos Pasos

- [ ] Integrar en rama main mediante PR
- [ ] Ejecutar primer workflow con análisis extendido
- [ ] Validar predicciones vs tendencias reales
- [ ] Ajustar SLOs según datos históricos
- [ ] (Opcional) Exportar métricas a Prometheus/Grafana

---

## 📞 Soporte

Para problemas o sugerencias:
1. Revisar `docs/AI_ANALYSIS.md`
2. Ejecutar `scripts/example_ai_analysis.py`
3. Verificar formato JSON de métricas

---

**Rama**: SELENEO  
**Fecha**: 2026-07-23  
**Estado**: Listo para PR a main
