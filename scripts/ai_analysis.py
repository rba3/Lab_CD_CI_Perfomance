#!/usr/bin/env python3
"""
AI Analysis Engine para Performance Testing
- Predicciones de degradación
- Recomendaciones automáticas
- Análisis de correlaciones entre endpoints
- Root cause analysis
"""

import json
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from collections import defaultdict
import statistics

class AIAnalysisEngine:
    """Motor de análisis con predicciones y correlaciones"""
    
    def __init__(self, current_metrics: Dict, historical_metrics: List[Dict] = None):
        """
        Args:
            current_metrics: Métricas actuales (JSON)
            historical_metrics: Histórico de corridas anteriores (JSON array)
        """
        self.current = current_metrics
        self.history = historical_metrics or []
        self.recommendations = []
        self.predictions = {}
        self.correlations = {}
        self.root_causes = []
    
    # ========== PREDICCIONES ==========
    
    def predict_degradation(self) -> Dict[str, Any]:
        """
        Analiza tendencias y predice posible degradación
        Retorna: {prediction, confidence, time_to_fail, risk_level}
        """
        if len(self.history) < 2:
            return {"prediction": "INSUFFICIENT_DATA", "confidence": 0}
        
        # Obtener últimas 5 corridas
        recent = self.history[-5:]
        
        # Extraer tendencias de latencia p95
        p95_values = []
        for run in recent:
            overall = run.get("overall", {})
            p95 = overall.get("p95_ms", 0)
            if p95 > 0:
                p95_values.append(p95)
        
        if len(p95_values) < 2:
            return {"prediction": "NO_TREND_DATA"}
        
        # Calcular pendiente (cambio por corrida)
        trend = p95_values[-1] - p95_values[0]
        runs_elapsed = len(p95_values) - 1
        slope = trend / runs_elapsed if runs_elapsed > 0 else 0
        
        # SLOs: PASS < 800, WARN 800-1500, FAIL > 1500
        current_p95 = self.current.get("overall", {}).get("p95_ms", 0)
        threshold_warn = 800
        threshold_fail = 1500
        
        risk = {
            "prediction": "STABLE",
            "confidence": 0,
            "slope_ms_per_run": round(slope, 2),
            "current_p95": current_p95,
            "days_to_warn": None,
            "days_to_fail": None,
            "risk_level": "LOW"
        }
        
        if slope > 0:  # Degradación
            # Estimar cuántas corridas hasta WARN/FAIL (asumiendo 1 corrida/día)
            if current_p95 < threshold_warn:
                runs_to_warn = (threshold_warn - current_p95) / slope if slope > 0 else float('inf')
                risk["days_to_warn"] = int(runs_to_warn)
                risk["prediction"] = "DEGRADATION_TREND"
                risk["confidence"] = min(90, int(runs_elapsed * 20))  # Confianza sube con más datos
            
            if current_p95 < threshold_fail:
                runs_to_fail = (threshold_fail - current_p95) / slope if slope > 0 else float('inf')
                risk["days_to_fail"] = int(runs_to_fail)
            
            # Clasificar riesgo
            if risk["days_to_fail"] and risk["days_to_fail"] < 7:
                risk["risk_level"] = "CRITICAL"
            elif risk["days_to_warn"] and risk["days_to_warn"] < 14:
                risk["risk_level"] = "HIGH"
            elif slope > 10:  # Crecimiento acelerado
                risk["risk_level"] = "MEDIUM"
            else:
                risk["risk_level"] = "LOW"
        
        self.predictions = risk
        return risk
    
    # ========== RECOMENDACIONES AUTOMÁTICAS ==========
    
    def generate_recommendations(self) -> List[Dict[str, str]]:
        """
        Genera recomendaciones específicas basadas en métricas
        """
        recommendations = []
        overall = self.current.get("overall", {})
        error_pct = overall.get("error_pct", 0)
        p95_ms = overall.get("p95_ms", 0)
        p50_ms = overall.get("p50_ms", 0)
        throughput = overall.get("throughput", 0)
        
        # Análisis por endpoint
        endpoints = self.current.get("endpoints", {})
        avg_p95 = statistics.mean([e.get("p95_ms", 0) for e in endpoints.values()]) if endpoints else 0
        
        for endpoint_name, ep_data in endpoints.items():
            ep_p95 = ep_data.get("p95_ms", 0)
            ep_error = ep_data.get("error_pct", 0)
            ep_throughput = ep_data.get("throughput", 0)
            
            # Endpoint lento
            if avg_p95 > 0 and ep_p95 > avg_p95 * 1.5:
                recommendations.append({
                    "endpoint": endpoint_name,
                    "issue": f"Latencia elevada (p95: {ep_p95}ms vs promedio: {avg_p95:.0f}ms)",
                    "severity": "HIGH",
                    "causes": [
                        "Base de datos no cacheada",
                        "Query compleja o N+1",
                        "API externa lenta (rate limiting?)",
                        "Recurso computacionalmente intensivo"
                    ],
                    "fixes": [
                        "Implementar caché (Redis/Memcached)",
                        "Optimizar query de BD",
                        "Usar CDN para contenido estático",
                        "Revisar últimos commits en PokeAPI"
                    ]
                })
            
            # Alta tasa de error
            if ep_error > 0.5:
                recommendations.append({
                    "endpoint": endpoint_name,
                    "issue": f"Tasa de error elevada ({ep_error}%)",
                    "severity": "CRITICAL",
                    "causes": [
                        "Response assertions fallando",
                        "Schema JSON cambió en PokeAPI",
                        "Validación de datos incorrecta",
                        "Timeout o conexión cerrada"
                    ],
                    "fixes": [
                        "Revisar últimos cambios en PokeAPI",
                        "Validar schema de respuestas",
                        "Aumentar timeout de conexión",
                        "Revisar logs de JMeter"
                    ]
                })
            
            # Throughput bajo
            avg_throughput = statistics.mean([e.get("throughput", 1) for e in endpoints.values()]) if endpoints else 1
            if ep_throughput < avg_throughput * 0.7:
                recommendations.append({
                    "endpoint": endpoint_name,
                    "issue": f"Throughput bajo ({ep_throughput:.1f} req/s vs {avg_throughput:.1f})",
                    "severity": "MEDIUM",
                    "causes": [
                        "Rate limiting de PokeAPI",
                        "Bottleneck de red",
                        "Contenedor con CPU limitado",
                        "Spike en latencia"
                    ],
                    "fixes": [
                        "Aumentar think time entre requests",
                        "Revisar límites de rate en PokeAPI",
                        "Escalas horizontalmente si es posible",
                        "Monitorear CPU/memoria del runner"
                    ]
                })
        
        # Análisis global
        if error_pct > 1:
            recommendations.insert(0, {
                "issue": "Tasa de error global crítica",
                "severity": "CRITICAL",
                "causes": [
                    "Problema sistémico (BD caída, network desconectada)",
                    "PokeAPI inestable",
                    "Assertions muy restrictivas"
                ],
                "fixes": [
                    "Revisar estado de PokeAPI (status.pokeapi.co)",
                    "Revisar logs de la corrida",
                    "Considerar relajar assertions",
                    "Abrir issue en PokeAPI si es su problema"
                ]
            })
        
        if p95_ms > 1500:
            recommendations.insert(0, {
                "issue": "Latencia crítica (p95 > 1500ms)",
                "severity": "CRITICAL",
                "causes": ["Ver análisis de endpoints específicos"],
                "fixes": ["Revisar recomendaciones por endpoint arriba"]
            })
        
        self.recommendations = recommendations
        return recommendations
    
    # ========== ANÁLISIS DE CORRELACIONES ==========
    
    def analyze_correlations(self) -> Dict[str, float]:
        """
        Detecta correlaciones entre endpoints (comparten recurso?)
        Retorna: {endpoint1_vs_endpoint2: correlation_score}
        """
        endpoints = self.current.get("endpoints", {})
        if len(endpoints) < 2:
            return {}
        
        correlations = {}
        
        # Comparar latencias entre pares de endpoints
        for ep1_name, ep1_data in endpoints.items():
            for ep2_name, ep2_data in endpoints.items():
                if ep1_name >= ep2_name:  # Evitar duplicados y self
                    continue
                
                # Usar p95 como métrica principal
                p95_1 = ep1_data.get("p95_ms", 0)
                p95_2 = ep2_data.get("p95_ms", 0)
                
                # Si ambos tienen datos históricos, calcular correlación
                if len(self.history) >= 3:
                    # Extraer series de p95 para cada endpoint
                    series_1 = []
                    series_2 = []
                    
                    for run in self.history[-7:]:  # Últimas 7 corridas
                        ep1_hist = run.get("endpoints", {}).get(ep1_name, {})
                        ep2_hist = run.get("endpoints", {}).get(ep2_name, {})
                        if ep1_hist.get("p95_ms") and ep2_hist.get("p95_ms"):
                            series_1.append(ep1_hist["p95_ms"])
                            series_2.append(ep2_hist["p95_ms"])
                    
                    if len(series_1) > 1:
                        correlation = self._pearson_correlation(series_1, series_2)
                        if correlation > 0.7:  # Solo mostrar correlaciones significativas
                            pair_key = f"{ep1_name} ↔ {ep2_name}"
                            correlations[pair_key] = round(correlation, 2)
        
        self.correlations = correlations
        return correlations
    
    @staticmethod
    def _pearson_correlation(x: List[float], y: List[float]) -> float:
        """Calcula correlación de Pearson entre dos series"""
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(len(x)))
        denom_x = sum((xi - mean_x) ** 2 for xi in x)
        denom_y = sum((yi - mean_y) ** 2 for yi in y)
        
        denominator = (denom_x * denom_y) ** 0.5
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    # ========== INTERPRETACIÓN DE CORRELACIONES ==========
    
    def interpret_correlations(self) -> List[str]:
        """Interpreta qué significan las correlaciones detectadas"""
        insights = []
        
        if not self.correlations:
            return ["✓ Endpoints independientes (no hay correlaciones fuertes)"]
        
        for pair, corr in sorted(self.correlations.items(), key=lambda x: x[1], reverse=True):
            if corr > 0.9:
                insights.append(
                    f"🔗 **{pair}** ({corr}): Muy correlacionados. "
                    f"Comparten infraestructura (DB, caché, o red). "
                    f"Problema en uno afecta al otro."
                )
            elif corr > 0.7:
                insights.append(
                    f"🔗 **{pair}** ({corr}): Correlacionados. "
                    f"Posible recurso compartido (caché, API). "
                    f"Monitorear patrones."
                )
        
        return insights
    
    # ========== ROOT CAUSE ANALYSIS ==========
    
    def identify_root_cause(self) -> Dict[str, Any]:
        """Identifica causa raíz probable de problemas"""
        overall = self.current.get("overall", {})
        error_pct = overall.get("error_pct", 0)
        p95_ms = overall.get("p95_ms", 0)
        p50_ms = overall.get("p50_ms", 0)
        
        root_cause = {
            "issue": None,
            "root_cause": None,
            "confidence": 0,
            "evidence": []
        }
        
        # Detectar patrón: si p95 >> p50, hay outliers/spikes
        if p50_ms > 0 and p95_ms / p50_ms > 3:
            root_cause["issue"] = "Latencia inconsistente (outliers)"
            root_cause["root_cause"] = "Spikes de latencia, posible GC o context switching"
            root_cause["confidence"] = 75
            root_cause["evidence"] = [
                f"p50 ({p50_ms}ms) mucho menor que p95 ({p95_ms}ms)",
                "Diferencia de 3x+ indica distribución anómala"
            ]
        
        # Todos los endpoints lentos → problema sistémico
        endpoints = self.current.get("endpoints", {})
        slow_count = sum(1 for e in endpoints.values() if e.get("p95_ms", 0) > 800)
        
        if len(endpoints) > 0 and slow_count == len(endpoints):
            root_cause["issue"] = "Problema sistémico"
            root_cause["root_cause"] = "PokeAPI lenta o conexión de red degradada"
            root_cause["confidence"] = 85
            root_cause["evidence"] = [
                f"Todos los {len(endpoints)} endpoints están lentos",
                "No es problema de endpoint específico"
            ]
        
        # Si solo algunos endpoints tienen error → problema específico
        error_endpoints = [name for name, data in endpoints.items() 
                          if data.get("error_pct", 0) > 0]
        if len(error_endpoints) > 0 and len(error_endpoints) < len(endpoints):
            root_cause["issue"] = "Problema en endpoint específico"
            root_cause["root_cause"] = f"Problema en: {', '.join(error_endpoints)}"
            root_cause["confidence"] = 80
            root_cause["evidence"] = [
                f"{len(error_endpoints)} de {len(endpoints)} endpoints con error",
                "Otros endpoints funcionan normalmente"
            ]
        
        self.root_causes = [root_cause]
        return root_cause
    
    # ========== EXPORTAR TODO ==========
    
    def to_dict(self) -> Dict[str, Any]:
        """Retorna análisis completo como diccionario"""
        return {
            "predictions": self.predictions,
            "recommendations": self.recommendations,
            "correlations": self.correlations,
            "root_cause": self.root_causes[0] if self.root_causes else {},
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def to_markdown(self) -> str:
        """Genera reporte en Markdown"""
        md = []
        
        # Predicciones
        if self.predictions:
            pred = self.predictions
            md.append("## 🔮 Predicciones\n")
            if pred.get("prediction") == "DEGRADATION_TREND":
                md.append(f"⚠️ **Tendencia de degradación detectada** ({pred.get('risk_level')} risk)")
                md.append(f"- Pendiente: +{pred.get('slope_ms_per_run')}ms/corrida")
                md.append(f"- P95 actual: {pred.get('current_p95')}ms")
                if pred.get("days_to_warn"):
                    md.append(f"- Días hasta WARN: ~{pred.get('days_to_warn')}")
                if pred.get("days_to_fail"):
                    md.append(f"- Días hasta FAIL: ~{pred.get('days_to_fail')}")
                md.append(f"- Confianza: {pred.get('confidence')}%\n")
            else:
                md.append(f"✓ {pred.get('prediction')}\n")
        
        # Recomendaciones
        if self.recommendations:
            md.append("## 💡 Recomendaciones Prioritarias\n")
            for i, rec in enumerate(self.recommendations[:5], 1):  # Top 5
                severity = rec.get("severity", "INFO")
                severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(severity, "ℹ️")
                
                md.append(f"{severity_icon} **{rec.get('issue', 'N/A')}**")
                if "endpoint" in rec:
                    md.append(f"   - Endpoint: `{rec['endpoint']}`")
                if rec.get("causes"):
                    md.append("   - Posibles causas: " + ", ".join(rec["causes"][:2]))
                if rec.get("fixes"):
                    md.append("   - Acciones: " + ", ".join(rec["fixes"][:2]))
                md.append("")
        
        # Correlaciones
        if self.correlations:
            md.append("## 🔗 Correlaciones Entre Endpoints\n")
            for insight in self.interpret_correlations():
                md.append(f"- {insight}")
            md.append("")
        
        # Root Cause
        if self.root_causes:
            root = self.root_causes[0]
            if root.get("issue"):
                md.append("## 🎯 Causa Raíz Identificada\n")
                md.append(f"**{root.get('issue')}**")
                md.append(f"- Causa probable: {root.get('root_cause')}")
                md.append(f"- Confianza: {root.get('confidence')}%")
                if root.get("evidence"):
                    md.append("- Evidencia:")
                    for ev in root["evidence"]:
                        md.append(f"  - {ev}")
                md.append("")
        
        return "\n".join(md)


def main():
    """CLI para análisis"""
    if len(sys.argv) < 2:
        print("Usage: python3 ai_analysis.py <current_metrics.json> [historical_metrics.json]")
        sys.exit(1)
    
    with open(sys.argv[1]) as f:
        current = json.load(f)
    
    historical = []
    if len(sys.argv) > 2:
        with open(sys.argv[2]) as f:
            historical = json.load(f)
    
    engine = AIAnalysisEngine(current, historical)
    engine.predict_degradation()
    engine.generate_recommendations()
    engine.analyze_correlations()
    engine.identify_root_cause()
    
    print(engine.to_markdown())
    print("\n<!-- JSON Analysis -->")
    print(json.dumps(engine.to_dict(), indent=2))


if __name__ == "__main__":
    main()
