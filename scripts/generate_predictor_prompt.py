#!/usr/bin/env python3
"""
Generador dinámico de prompt para el Agente Predictivo Avanzado
Inserta datos reales del histórico y métricas actuales
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

def generate_predictor_prompt(
    metrics_file: str,
    historical_file: str,
    template_file: str = "prompts/prompt-predictor-template.txt",
    output_file: str = None
) -> str:
    """
    Genera prompt dinámico reemplazando placeholders con datos reales
    
    Args:
        metrics_file: Archivo JSON de métricas actuales
        historical_file: Archivo JSON con histórico
        template_file: Template del prompt
        output_file: Archivo de salida (opcional)
    
    Returns:
        Prompt generado como string
    """
    
    # Leer datos
    with open(metrics_file) as f:
        current_metrics = json.load(f)
    
    with open(historical_file) as f:
        historical_data = json.load(f)
    
    with open(template_file) as f:
        template = f.read()
    
    # Preparar datos históricos resumidos (últimas 7-14 corridas)
    recent_history = historical_data[-14:] if len(historical_data) > 14 else historical_data
    
    historical_summary = prepare_historical_summary(recent_history)
    metrics_summary = prepare_metrics_summary(current_metrics)
    
    # Reemplazar placeholders
    prompt = template.replace("{HISTORICAL_DATA}", json.dumps(historical_summary, indent=2))
    prompt = prompt.replace("{CURRENT_METRICS}", json.dumps(metrics_summary, indent=2))
    
    # Agregar contexto adicional
    prompt = add_contextual_info(prompt, current_metrics, historical_data)
    
    # Guardar si se especifica
    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(prompt)
        print(f"✅ Prompt guardado en: {output_file}")
    
    return prompt


def prepare_historical_summary(historical_data: list) -> dict:
    """
    Prepara resumen del histórico para el agente
    Incluye tendencias, patrones, estadísticas
    """
    if not historical_data:
        return {}
    
    summary = {
        "total_runs": len(historical_data),
        "date_range": f"{historical_data[0].get('timestamp', 'N/A')} a {historical_data[-1].get('timestamp', 'N/A')}",
        "runs": []
    }
    
    # Extraer datos de cada corrida (últimas 14)
    for i, run in enumerate(historical_data[-14:], 1):
        overall = run.get("overall", {})
        summary["runs"].append({
            "run_number": i,
            "timestamp": run.get("timestamp", "N/A"),
            "p50_ms": overall.get("p50_ms", 0),
            "p95_ms": overall.get("p95_ms", 0),
            "p99_ms": overall.get("p99_ms", 0),
            "error_pct": overall.get("error_pct", 0),
            "throughput": overall.get("throughput", 0),
            "sample_count": overall.get("sample_count", 0)
        })
    
    # Calcular estadísticas
    p95_values = [r.get("overall", {}).get("p95_ms", 0) for r in historical_data if r.get("overall", {}).get("p95_ms")]
    error_values = [r.get("overall", {}).get("error_pct", 0) for r in historical_data if r.get("overall", {}).get("error_pct") is not None]
    
    if p95_values:
        summary["p95_statistics"] = {
            "min": min(p95_values),
            "max": max(p95_values),
            "avg": round(sum(p95_values) / len(p95_values), 2),
            "latest": p95_values[-1],
            "trend": "DEGRADING" if len(p95_values) > 1 and p95_values[-1] > p95_values[0] else "IMPROVING" if len(p95_values) > 1 and p95_values[-1] < p95_values[0] else "STABLE"
        }
    
    if error_values:
        summary["error_statistics"] = {
            "min": min(error_values),
            "max": max(error_values),
            "avg": round(sum(error_values) / len(error_values), 2),
            "latest": error_values[-1]
        }
    
    return summary


def prepare_metrics_summary(metrics: dict) -> dict:
    """
    Prepara resumen de métricas actuales
    """
    overall = metrics.get("overall", {})
    endpoints = metrics.get("endpoints", {})
    
    summary = {
        "overall": {
            "p50_ms": overall.get("p50_ms", 0),
            "p95_ms": overall.get("p95_ms", 0),
            "p99_ms": overall.get("p99_ms", 0),
            "error_pct": overall.get("error_pct", 0),
            "throughput": overall.get("throughput", 0),
            "sample_count": overall.get("sample_count", 0)
        },
        "endpoints_summary": {}
    }
    
    # Resumen por endpoint
    for endpoint_name, ep_data in endpoints.items():
        summary["endpoints_summary"][endpoint_name] = {
            "p50_ms": ep_data.get("p50_ms", 0),
            "p95_ms": ep_data.get("p95_ms", 0),
            "p99_ms": ep_data.get("p99_ms", 0),
            "error_pct": ep_data.get("error_pct", 0),
            "throughput": ep_data.get("throughput", 0)
        }
    
    return summary


def add_contextual_info(prompt: str, metrics: dict, historical: list) -> str:
    """
    Agrega contexto adicional al prompt basado en datos
    """
    context = "\n\n### CONTEXTO ADICIONAL:\n"
    
    overall = metrics.get("overall", {})
    p95 = overall.get("p95_ms", 0)
    error_pct = overall.get("error_pct", 0)
    
    # Contexto de umbral
    context += "\n**Estado vs SLOs:**\n"
    if p95 < 800:
        context += f"✅ Latencia DENTRO de SLO (p95={p95}ms < 800ms)\n"
    elif p95 < 1500:
        context += f"⚠️ Latencia EN ADVERTENCIA (p95={p95}ms, SLO=800ms)\n"
    else:
        context += f"❌ Latencia CRÍTICA (p95={p95}ms > 1500ms)\n"
    
    if error_pct < 0.1:
        context += f"✅ Error rate BAJO ({error_pct}% < 0.1%)\n"
    elif error_pct < 1:
        context += f"⚠️ Error rate MODERADO ({error_pct}%, SLO=<1%)\n"
    else:
        context += f"❌ Error rate CRÍTICO ({error_pct}% > 1%)\n"
    
    # Contexto de cambio reciente
    if len(historical) > 1:
        last_run = historical[-1].get("overall", {})
        last_p95 = last_run.get("p95_ms", 0)
        
        if last_p95 > 0:
            change_pct = ((p95 - last_p95) / last_p95) * 100
            if abs(change_pct) > 10:
                direction = "AUMENTÓ" if change_pct > 0 else "DISMINUYÓ"
                context += f"\n**Cambio vs última corrida:** {direction} {abs(change_pct):.1f}%\n"
    
    # Contexto de hora del día (si está disponible)
    now = datetime.utcnow()
    context += f"\n**Momento de análisis:** {now.strftime('%Y-%m-%d %H:%M UTC')} (día de semana: {now.strftime('%A')})\n"
    
    return prompt + context


def main():
    """CLI para generar prompt dinámico"""
    if len(sys.argv) < 3:
        print("Usage: python3 generate_predictor_prompt.py <metrics.json> <historical.json> [--output prompt.txt] [--template template.txt]")
        sys.exit(1)
    
    metrics_file = sys.argv[1]
    historical_file = sys.argv[2]
    
    output_file = None
    template_file = "prompts/prompt-predictor-template.txt"
    
    # Parsear argumentos opcionales
    if "--output" in sys.argv:
        idx = sys.argv.index("--output") + 1
        if idx < len(sys.argv):
            output_file = sys.argv[idx]
    
    if "--template" in sys.argv:
        idx = sys.argv.index("--template") + 1
        if idx < len(sys.argv):
            template_file = sys.argv[idx]
    
    # Generar prompt
    prompt = generate_predictor_prompt(
        metrics_file,
        historical_file,
        template_file,
        output_file
    )
    
    # Imprimir
    print("=" * 70)
    print("PROMPT GENERADO PARA AGENTE PREDICTIVO")
    print("=" * 70)
    print(prompt)
    
    return prompt


if __name__ == "__main__":
    main()
