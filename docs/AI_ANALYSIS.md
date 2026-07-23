# 📊 Análisis Extendido de Performance - Documentación

## 🎯 Overview

El laboratorio ahora incluye un motor de análisis avanzado que proporciona:

- **🔮 Predicciones de degradación** - Detecta tendencias y predice cuándo se alcanzarán los SLOs
- **💡 Recomendaciones automáticas** - Sugerencias específicas por endpoint
- **🔗 Análisis de correlaciones** - Identifica recursos compartidos entre endpoints
- **🎯 Root cause analysis** - Diagnóstico automático de problemas

## 📦 Componentes

### 1. `scripts/ai_analysis.py`
Motor principal de análisis con la clase `AIAnalysisEngine`

**Métodos principales:**
```python
engine = AIAnalysisEngine(current_metrics, historical_metrics)

# Predicciones
engine.predict_degradation()  # → Dict con riesgo, días a FAIL, etc.

# Recomendaciones
engine.generate_recommendations()  # → List de recomendaciones

# Correlaciones
engine.analyze_correlations()  # → Dict con pares de endpoints correlacionados

# Causa raíz
engine.identify_root_cause()  # → Dict con problema detectado

# Exportar
engine.to_markdown()  # → String Markdown
engine.to_dict()      # → Dict JSON
```

### 2. `scripts/gen_report_enhanced.py`
Generador de reportes mejorado que integra el análisis extendido

**Uso:**
```bash
python3 scripts/gen_report_enhanced.py \
  --metrics reports/metrics-consolidated.json \
  --verdict verdict.md \
  --date "2026-07-24 10:30 UTC" \
  --run-url "https://github.com/rba3/Lab_CD_CI_Perfomance/actions/runs/12345" \
  --historical reports/historical.json \
  --out reports/report-2026-07-24_1030.md
```

### 3. `scripts/example_ai_analysis.py`
Ejemplos de uso locales para testing y desarrollo

## 🔄 Flujo en GitHub Actions

El workflow mejorado ahora:

1. **Ejecuta JMeter** (sin cambios)
2. **Calcula métricas** (sin cambios)
3. **Agente IA** valida contra SLOs (sin cambios)
4. **→ NUEVO:** Carga histórico de corridas anteriores
5. **→ NUEVO:** Ejecuta análisis extendido:
   - Detecta tendencias
   - Genera recomendaciones
   - Analiza correlaciones
   - Identifica causa raíz
6. **→ NUEVO:** Genera reporte mejorado con todo integrado
7. **→ NUEVO:** Actualiza histórico (últimas 30 corridas)
8. Abre issue si hay WARN/FAIL (ahora con análisis extendido)

## 📊 Ejemplo de Salida

### Predicciones
```
🔮 Predicciones

⚠️ Tendencia de degradación detectada (HIGH risk)
- Pendiente: +0.5ms/corrida
- P95 actual: 475ms
- Días hasta WARN: ~10
- Días hasta FAIL: ~25
- Confianza: 85%
```

### Recomendaciones
```
💡 Recomendaciones Prioritarias

🔴 Tasa de error elevada (1.2%)
   - Endpoint: type
   - Posibles causas: Schema JSON cambió, Timeout o conexión cerrada
   - Acciones: Revisar últimos cambios en PokeAPI, Aumentar timeout

🟠 Latencia elevada (p95: 550ms vs promedio: 437ms)
   - Endpoint: type
   - Posibles causas: Query compleja, API externa lenta
   - Acciones: Implementar caché, Optimizar query de BD
```

### Correlaciones
```
🔗 Correlaciones Entre Endpoints

- 🔗 pokemon ↔ type (0.95): Muy correlacionados
  Comparten infraestructura. Problema en uno afecta al otro.
```

### Causa Raíz
```
🎯 Causa Raíz Identificada

Problema en endpoint específico
- Causa probable: Problema en: type
- Confianza: 80%
- Evidencia:
  - 1 de 2 endpoints con error
  - Otro endpoint funciona normalmente
```

## 🚀 Cómo Usar Localmente

### Testing rápido
```bash
cd scripts
python3 example_ai_analysis.py
```

Esto genera ejemplos sin datos reales.

### Con datos reales
```bash
# Después de ejecutar JMeter localmente:
python3 scripts/ai_analysis.py \
  reports/metrics-smoke.json \
  reports/historical.json

# Generar reporte completo:
python3 scripts/gen_report_enhanced.py \
  --metrics reports/metrics-smoke.json \
  --verdict verdict.md \
  --out reports/test-report.md
```

## 📈 Interpretación de Resultados

### Predicción: DEGRADATION_TREND
**Significa:** El p95 ha estado subiendo consistentemente

**Acciones:**
- Revisar commits recientes en PokeAPI
- Monitorear si sigue la tendencia
- Si llega a WARN, investigar cambios en infraestructura

**Riesgo:**
- `LOW`: Crecimiento lento, tiempo suficiente
- `MEDIUM`: Crecimiento moderado, revisar pronto
- `HIGH`: Crecimiento rápido, requiere atención
- `CRITICAL`: Alcanzará FAIL en < 7 días

### Correlación > 0.9
**Significa:** Dos endpoints suben/bajan juntos, comparten recurso

**Investigar:**
- ¿Comparten BD?
- ¿Caché compartido?
- ¿Misma región/servidor?

Si afecta a uno, probablemente afecte al otro.

### Correlación 0.7-0.9
**Significa:** Ligada correlación, posible dependencia indirecta

**Investigar:**
- Flow de datos entre endpoints
- Rate limiting compartido
- Recursos de red

## ⚙️ Personalización

### Cambiar SLOs
En `ai_analysis.py`, función `generate_recommendations()`:
```python
threshold_warn = 800    # Cambiar si es necesario
threshold_fail = 1500   # Cambiar si es necesario
```

### Ajustar sensibilidad de predicciones
En `predict_degradation()`:
```python
# Actualmente usa últimas 5 corridas
recent = self.history[-5:]

# Cambiar a más corridas para más confianza:
recent = self.history[-10:]
```

### Cambiar límite de histórico
En workflow `.github/workflows/perf-tests.yml`:
```bash
# Actualmente mantiene 30 corridas
TRIMMED=$(echo "$UPDATED" | jq '.[-30:]')

# Cambiar a 60 corridas:
TRIMMED=$(echo "$UPDATED" | jq '.[-60:]')
```

## 🔍 Troubleshooting

### "INSUFFICIENT_DATA" en predicciones
- Solución: Ejecutar el workflow al menos 3 veces
- Necesita histórico para detectar tendencias

### Correlaciones vacías
- Normal si hay < 2 endpoints
- Si hay múltiples endpoints, revisar que los datos sean válidos

### "Agente de IA no disponible"
- Fallback a veredicto por umbrales automáticamente
- Análisis extendido sigue funcionando igual

## 📝 Ejemplo de Reporte Completo

Ver en: `reports/report-YYYY-MM-DD_HHMM.md`

Estructura:
1. Veredicto del Agente IA
2. Predicciones
3. Recomendaciones Prioritarias
4. Correlaciones
5. Causa Raíz
6. Métricas Globales
7. Rendimiento por Endpoint
8. Gráfico de Tendencia Histórica
9. JSON Técnico

## 🎓 Referencias

- **Correlación de Pearson:** Mide relación lineal entre dos variables (-1 a 1)
  - > 0.9: Muy correlacionados
  - 0.7-0.9: Correlacionados
  - < 0.7: Débilmente correlacionados

- **Percentiles:**
  - p50: Mediana (50% de requests son más rápidas)
  - p95: 95% de requests son más rápidas (5% más lentas)
  - p99: 99% de requests son más rápidas (1% outliers)

## 🤝 Contribuir

¿Ideas para mejorar el análisis?
- Agregar más heurísticas
- Mejorar detección de causa raíz
- Nuevo tipo de análisis

Crea un PR o issue! 🚀
