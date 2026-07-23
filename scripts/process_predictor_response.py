#!/usr/bin/env python3
"""
Procesador de respuesta del Agente Predictivo Avanzado
Formatea y enriquece el análisis predictivo de IA
"""

import json
import sys
from pathlib import Path
from datetime import datetime

def parse_predictor_response(response_text: str, metrics: dict, historical: list) -> dict:
    """
    Procesa respuesta del agente predictivo y extrae insights
    
    Args:
        response_text: Respuesta del agente IA
        metrics: Métricas actuales
        historical: Histórico de corridas
    
    Returns:
        Dict con análisis enriquecido
    """
    
    analysis = {
        "timestamp": datetime.utcnow().isoformat(),
        "raw_response": response_text,
        "extracted_insights": extract_insights(response_text),
        "patterns_detected": detect_patterns(historical),
        "anomalies": detect_anomalies(metrics, historical),
        "forecast": generate_forecast(historical),
        "recommendations": prioritize_recommendations(response_text)
    }
    
    return analysis


def extract_insights(response_text: str) -> dict:
    """Extrae insights clave de la respuesta del agente"""
    insights = {
        "is_degrading": False,
        "is_stable": False,
        "is_improving": False,
        "has_anomalies": False,
        "has_patterns": False,
        "key_findings": []
    }
    
    # Palabras clave para detectar estados
    degradation_keywords = ["degrada", "empeor", "sube", "aumenta", "alarma", "crítico", "cuidado"]
    improvement_keywords = ["mejora", "baja", "optimiza", "estable", "normal", "bien"]
    anomaly_keywords = ["anomalía", "inusual", "outlier", "extraño", "pico", "spike"]
    pattern_keywords = ["patrón", "ciclo", "recurrente", "periódico", "predecible"]
    
    text_lower = response_text.lower()
    
    for keyword in degradation_keywords:
        if keyword in text_lower:
            insights["is_degrading"] = True
            break
    
    for keyword in improvement_keywords:
        if keyword in text_lower:
            insights["is_improving"] = True
            break
    
    for keyword in anomaly_keywords:
        if keyword in text_lower:
            insights["has_anomalies"] = True
            break
    
    for keyword in pattern_keywords:
        if keyword in text_lower:
            insights["has_patterns"] = True
            break
    
    if not any([insights["is_degrading"], insights["is_improving"]]):
        insights["is_stable"] = True
    
    # Extraer líneas importantes (heurística: líneas que empiezan con -,*,•)
    for line in response_text.split('\n'):
        line = line.strip()
        if line and line[0] in ['-', '*', '•']:
            insights["key_findings"].append(line[1:].strip())
    
    return insights


def detect_patterns(historical: list) -> dict:
    """Detecta patrones en datos históricos"""
    if len(historical) < 7:
        return {"status": "INSUFFICIENT_DATA", "patterns": []}
    
    patterns = {
        "status": "ANALYZED",
        "patterns": [],
        "weekly_cycle": None,
        "trending": None
    }
    
    # Extraer últimas 7-30 corridas
    recent = historical[-30:] if len(historical) >= 30 else historical
    
    p95_values = [run.get("overall", {}).get("p95_ms", 0) for run in recent if run.get("overall", {}).get("p95_ms")]
    
    if len(p95_values) >= 7:
        # Detectar si hay ciclo semanal (cada 7 corridas)
        if len(p95_values) >= 14:
            week1_avg = sum(p95_values[0:7]) / 7
            week2_avg = sum(p95_values[7:14]) / 7
            
            if abs(week1_avg - week2_avg) / week1_avg < 0.15:  # Similar semana a semana
                patterns["weekly_cycle"] = {
                    "detected": True,
                    "week1_avg": round(week1_avg, 2),
                    "week2_avg": round(week2_avg, 2),
                    "confidence": 0.7
                }
                patterns["patterns"].append("Ciclo semanal detectado")
        
        # Detectar tendencia general
        first_half = sum(p95_values[:len(p95_values)//2]) / (len(p95_values)//2)
        second_half = sum(p95_values[len(p95_values)//2:]) / (len(p95_values) - len(p95_values)//2)
        
        change_pct = ((second_half - first_half) / first_half) * 100
        
        if abs(change_pct) > 10:
            direction = "DEGRADING" if change_pct > 0 else "IMPROVING"
            patterns["trending"] = {
                "direction": direction,
                "change_percentage": round(change_pct, 2),
                "severity": "HIGH" if abs(change_pct) > 30 else "MEDIUM" if abs(change_pct) > 15 else "LOW"
            }
            patterns["patterns"].append(f"Tendencia: {direction} ({change_pct:+.1f}%)")
    
    return patterns


def detect_anomalies(metrics: dict, historical: list) -> dict:
    """Detecta anomalías en datos actuales vs histórico"""
    if not historical or not metrics:
        return {"anomalies": []}
    
    anomalies = {
        "detected_count": 0,
        "anomalies": []
    }
    
    current_p95 = metrics.get("overall", {}).get("p95_ms", 0)
    current_error = metrics.get("overall", {}).get("error_pct", 0)
    
    if not historical:
        return anomalies
    
    # Calcular promedio histórico
    hist_p95 = [r.get("overall", {}).get("p95_ms", 0) for r in historical if r.get("overall", {}).get("p95_ms")]
    hist_error = [r.get("overall", {}).get("error_pct", 0) for r in historical if r.get("overall", {}).get("error_pct") is not None]
    
    if hist_p95:
        avg_p95 = sum(hist_p95) / len(hist_p95)
        max_hist_p95 = max(hist_p95)
        std_dev_p95 = (sum((x - avg_p95)**2 for x in hist_p95) / len(hist_p95))**0.5 if len(hist_p95) > 1 else 0
        
        # Detectar spike (> 2 desviaciones estándar)
        if std_dev_p95 > 0 and current_p95 > avg_p95 + (2 * std_dev_p95):
            anomalies["anomalies"].append({
                "type": "LATENCY_SPIKE",
                "severity": "HIGH",
                "current": current_p95,
                "average": round(avg_p95, 2),
                "z_score": round((current_p95 - avg_p95) / std_dev_p95, 2)
            })
            anomalies["detected_count"] += 1
    
    if hist_error:
        avg_error = sum(hist_error) / len(hist_error)
        
        if current_error > avg_error * 2:
            anomalies["anomalies"].append({
                "type": "ERROR_SPIKE",
                "severity": "CRITICAL",
                "current": current_error,
                "average": round(avg_error, 2)
            })
            anomalies["detected_count"] += 1
    
    return anomalies


def generate_forecast(historical: list) -> dict:
    """Genera pronóstico para próximas 7 corridas"""
    if len(historical) < 3:
        return {"status": "INSUFFICIENT_DATA"}
    
    recent = historical[-7:]
    p95_values = [r.get("overall", {}).get("p95_ms", 0) for r in recent if r.get("overall", {}).get("p95_ms")]
    
    if len(p95_values) < 2:
        return {"status": "INSUFFICIENT_DATA"}
    
    # Calcular pendiente (cambio por corrida)
    slope = (p95_values[-1] - p95_values[0]) / (len(p95_values) - 1)
    
    forecast = {
        "status": "FORECASTED",
        "current": p95_values[-1],
        "slope": round(slope, 2),
        "next_7_days": []
    }
    
    for day in range(1, 8):
        predicted = p95_values[-1] + (slope * day)
        forecast["next_7_days"].append({
            "day": day,
            "predicted_p95": round(predicted, 2),
            "status": "PASS" if predicted < 800 else "WARN" if predicted < 1500 else "FAIL"
        })
    
    return forecast


def prioritize_recommendations(response_text: str) -> list:
    """Extrae y prioriza recomendaciones de la respuesta del agente"""
    recommendations = []
    
    # Buscar líneas con recomendaciones (heurística)
    recommendation_keywords = ["recomend", "sugerir", "implementar", "revisar", "aumentar", "reducir", "monitorear"]
    
    for line in response_text.split('\n'):
        line = line.strip()
        if any(keyword in line.lower() for keyword in recommendation_keywords):
            # Priorizar según urgencia
            priority = "MEDIUM"
            if any(w in line.lower() for w in ["crítico", "urgente", "inmediato", "ahora"]):
                priority = "HIGH"
            elif any(w in line.lower() for w in ["considerar", "futuro", "largo plazo"]):
                priority = "LOW"
            
            recommendations.append({
                "text": line,
                "priority": priority
            })
    
    # Ordenar por prioridad
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    recommendations.sort(key=lambda x: priority_order[x["priority"]])
    
    return recommendations


def generate_markdown_report(analysis: dict) -> str:
    """Genera reporte en Markdown del análisis predictivo"""
    md = []
    
    md.append("## 🔮 Análisis Predictivo Avanzado (IA)\n")
    
    # Insights principales
    insights = analysis.get("extracted_insights", {})
    if insights:
        status_emoji = "📈" if insights.get("is_degrading") else "📉" if insights.get("is_improving") else "➡️"
        status_text = "Degradación" if insights.get("is_degrading") else "Mejora" if insights.get("is_improving") else "Estable"
        
        md.append(f"**Estado General:** {status_emoji} {status_text}\n")
        
        if insights.get("has_patterns"):
            md.append("⚠️ Se detectaron **patrones cíclicos**\n")
        
        if insights.get("has_anomalies"):
            md.append("🚨 Se detectaron **anomalías**\n")
        
        if insights.get("key_findings"):
            md.append("**Hallazgos Clave:**\n")
            for finding in insights["key_findings"][:5]:  # Top 5
                md.append(f"- {finding}")
            md.append("")
    
    # Patrones detectados
    patterns = analysis.get("patterns_detected", {})
    if patterns.get("patterns"):
        md.append("**Patrones Detectados:**\n")
        for pattern in patterns["patterns"]:
            md.append(f"- {pattern}")
        md.append("")
    
    # Anomalías
    anomalies = analysis.get("anomalies", {})
    if anomalies.get("detected_count", 0) > 0:
        md.append("**Anomalías Detectadas:**\n")
        for anomaly in anomalies["anomalies"]:
            severity = anomaly.get("severity", "INFO")
            icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(severity, "ℹ️")
            md.append(f"{icon} {anomaly['type']}: {anomaly.get('current', 'N/A')}")
        md.append("")
    
    # Pronóstico
    forecast = analysis.get("forecast", {})
    if forecast.get("status") == "FORECASTED":
        md.append("**Pronóstico (Próximos 7 días):**\n")
        md.append("| Día | P95 Predicho | Estado |")
        md.append("|-----|--------------|--------|")
        for day_forecast in forecast.get("next_7_days", [])[:7]:
            md.append(
                f"| {day_forecast['day']} | {day_forecast['predicted_p95']}ms | {day_forecast['status']} |"
            )
        md.append("")
    
    # Recomendaciones
    recommendations = analysis.get("recommendations", [])
    if recommendations:
        md.append("**Recomendaciones Priorizadas:**\n")
        for i, rec in enumerate(recommendations[:5], 1):
            priority_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}.get(rec.get("priority"), "ℹ️")
            md.append(f"{i}. {priority_icon} {rec['text']}")
        md.append("")
    
    # Respuesta cruda del agente
    md.append("**Análisis Detallado del Agente IA:**\n")
    md.append("```")
    md.append(analysis.get("raw_response", "Sin respuesta del agente"))
    md.append("```\n")
    
    return "\n".join(md)


def main():
    """CLI para procesar respuesta del agente predictivo"""
    if len(sys.argv) < 2:
        print("Usage: python3 process_predictor_response.py <ai_response.txt> [metrics.json] [historical.json] [--output out.md]")
        sys.exit(1)
    
    # Leer respuesta del agente
    response_file = sys.argv[1]
    with open(response_file) as f:
        response_text = f.read()
    
    # Leer métricas (opcional)
    metrics = {}
    if len(sys.argv) > 2 and Path(sys.argv[2]).exists():
        with open(sys.argv[2]) as f:
            metrics = json.load(f)
    
    # Leer histórico (opcional)
    historical = []
    if len(sys.argv) > 3 and Path(sys.argv[3]).exists():
        with open(sys.argv[3]) as f:
            historical = json.load(f)
    
    # Procesar
    analysis = parse_predictor_response(response_text, metrics, historical)
    
    # Generar reporte
    markdown = generate_markdown_report(analysis)
    
    # Guardar si se especifica salida
    if "--output" in sys.argv:
        output_idx = sys.argv.index("--output") + 1
        if output_idx < len(sys.argv):
            output_file = sys.argv[output_idx]
            Path(output_file).parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                f.write(markdown)
            print(f"✅ Reporte guardado en: {output_file}")
    
    # Imprimir
    print(markdown)
    
    # Guardar JSON
    json_output = response_file.replace(".txt", ".json")
    with open(json_output, "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"✅ Análisis JSON guardado en: {json_output}")


if __name__ == "__main__":
    main()
