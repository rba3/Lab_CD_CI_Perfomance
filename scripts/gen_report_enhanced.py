#!/usr/bin/env python3
"""
Generador de reporte Markdown mejorado con análisis de IA extendido
Integra predicciones, recomendaciones y correlaciones
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from ai_analysis import AIAnalysisEngine

def generate_report(
    metrics_files: list,
    verdict_file: str = None,
    date_str: str = None,
    run_url: str = None,
    historical_file: str = None,
    output_file: str = None
) -> str:
    """
    Genera reporte completo con análisis extendido
    
    Args:
        metrics_files: Lista de archivos de métricas JSON
        verdict_file: Archivo con veredicto del agente IA
        date_str: Fecha en formato legible
        run_url: URL de la corrida en GitHub Actions
        historical_file: Archivo JSON con histórico de corridas
        output_file: Archivo de salida
    
    Returns:
        Contenido del reporte en Markdown
    """
    
    # Cargar métricas actuales
    metrics = {}
    for metrics_file in metrics_files:
        with open(metrics_file) as f:
            data = json.load(f)
            # Merge de métricas (en caso de múltiples escenarios)
            if "overall" in data:
                metrics = data  # Usar la última (asume consolidación)
    
    # Cargar histórico si existe
    historical = []
    if historical_file and Path(historical_file).exists():
        with open(historical_file) as f:
            historical = json.load(f)
    
    # Cargar veredicto del agente IA
    verdict_text = "Veredicto no disponible"
    if verdict_file and Path(verdict_file).exists():
        with open(verdict_file) as f:
            verdict_text = f.read().strip()
    
    # Inicializar motor de análisis
    engine = AIAnalysisEngine(metrics, historical)
    engine.predict_degradation()
    engine.generate_recommendations()
    engine.analyze_correlations()
    engine.identify_root_cause()
    
    # Construir reporte
    report = []
    report.append("# 📊 Reporte de Performance - PokeAPI\n")
    
    # Header con información básica
    if date_str:
        report.append(f"**Fecha de corrida:** {date_str}\n")
    if run_url:
        report.append(f"**Enlace:** [{run_url.split('/')[-1]}]({run_url})\n")
    
    # ===== VEREDICTO DEL AGENTE IA =====
    report.append("## ✅ Veredicto\n")
    report.append(f"```\n{verdict_text}\n```\n")
    
    # ===== ANÁLISIS EXTENDIDO =====
    report.append(engine.to_markdown())
    
    # ===== MÉTRICAS GLOBALES =====
    overall = metrics.get("overall", {})
    report.append("## 📈 Métricas Globales\n")
    report.append("| Métrica | Valor | SLO | Estado |")
    report.append("|---------|-------|-----|--------|")
    
    error_pct = overall.get("error_pct", 0)
    p95_ms = overall.get("p95_ms", 0)
    p50_ms = overall.get("p50_ms", 0)
    p99_ms = overall.get("p99_ms", 0)
    throughput = overall.get("throughput", 0)
    
    status_error = "✅ PASS" if error_pct < 0.1 else "⚠️ WARN" if error_pct < 1 else "❌ FAIL"
    status_p95 = "✅ PASS" if p95_ms < 800 else "⚠️ WARN" if p95_ms < 1500 else "❌ FAIL"
    
    report.append(f"| Error Rate | {error_pct}% | < 0.1% | {status_error} |")
    report.append(f"| Latencia p50 | {p50_ms}ms | - | ℹ️ |")
    report.append(f"| Latencia p95 | {p95_ms}ms | < 800ms | {status_p95} |")
    report.append(f"| Latencia p99 | {p99_ms}ms | - | ℹ️ |")
    report.append(f"| Throughput | {throughput:.2f} req/s | - | ℹ️ |")
    report.append(f"| Muestras | {overall.get('sample_count', 0)} | - | ℹ️ |\n")
    
    # ===== MÉTRICAS POR ENDPOINT =====
    endpoints = metrics.get("endpoints", {})
    if endpoints:
        report.append("## 🎯 Rendimiento por Endpoint\n")
        report.append("| Endpoint | p50 | p95 | p99 | Error | Throughput |")
        report.append("|----------|-----|-----|-----|-------|------------|")
        
        for endpoint_name, ep_data in sorted(endpoints.items()):
            ep_p50 = ep_data.get("p50_ms", 0)
            ep_p95 = ep_data.get("p95_ms", 0)
            ep_p99 = ep_data.get("p99_ms", 0)
            ep_error = ep_data.get("error_pct", 0)
            ep_throughput = ep_data.get("throughput", 0)
            
            error_indicator = "❌" if ep_error > 0.5 else "⚠️" if ep_error > 0 else "✅"
            
            report.append(
                f"| {endpoint_name} | {ep_p50}ms | {ep_p95}ms | {ep_p99}ms | {error_indicator} {ep_error}% | {ep_throughput:.2f} req/s |"
            )
        
        report.append("")
    
    # ===== GRÁFICO MERMAID DE TENDENCIA (si hay datos históricos) =====
    if len(historical) >= 3:
        report.append("## 📉 Tendencia Histórica (Últimas 7 corridas)\n")
        report.append("```mermaid")
        report.append("graph LR")
        
        recent = historical[-7:]
        for i, run in enumerate(recent):
            overall_run = run.get("overall", {})
            p95_val = overall_run.get("p95_ms", 0)
            timestamp = run.get("timestamp", f"Corrida {i+1}")[-5:]  # Últimos 5 chars
            report.append(f"    C{i}['{timestamp}<br/>{p95_val}ms']")
            
            if i > 0:
                # Conectar puntos
                prev_p95 = recent[i-1].get("overall", {}).get("p95_ms", 0)
                if p95_val > prev_p95 * 1.1:
                    report.append(f"    C{i-1} -->|📈 +| C{i}")
                elif p95_val < prev_p95 * 0.9:
                    report.append(f"    C{i-1} -->|📉 -| C{i}")
                else:
                    report.append(f"    C{i-1} --> C{i}")
        
        report.append("```\n")
    
    # ===== JSON DE ANÁLISIS (para máquinas) =====
    report.append("## 🔧 Análisis Técnico Detallado (JSON)\n")
    analysis_json = engine.to_dict()
    report.append("```json")
    report.append(json.dumps(analysis_json, indent=2))
    report.append("```\n")
    
    # ===== MÉTRICAS BRUTAS =====
    report.append("## 📦 Datos Completos (JSON)\n")
    report.append("```json")
    report.append(json.dumps(metrics, indent=2))
    report.append("```\n")
    
    # ===== FOOTER =====
    report.append("---\n")
    report.append("*Reporte generado automáticamente por el workflow de performance.*\n")
    report.append(f"*Timestamp: {datetime.utcnow().isoformat()}Z*\n")
    
    # Guardar archivo
    report_content = "\n".join(report)
    if output_file:
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w") as f:
            f.write(report_content)
        print(f"✅ Reporte guardado en: {output_file}")
    
    return report_content


def main():
    parser = argparse.ArgumentParser(
        description="Generador de reporte de performance con análisis extendido"
    )
    parser.add_argument("--metrics", nargs="+", required=True,
                       help="Archivos JSON de métricas")
    parser.add_argument("--verdict", help="Archivo con veredicto del agente IA")
    parser.add_argument("--date", help="Fecha en formato legible (ej: 2026-07-24 10:30 UTC)")
    parser.add_argument("--run-url", help="URL de la corrida en GitHub Actions")
    parser.add_argument("--historical", help="Archivo JSON con histórico de corridas")
    parser.add_argument("--out", required=True, help="Archivo de salida")
    
    args = parser.parse_args()
    
    report_content = generate_report(
        metrics_files=args.metrics,
        verdict_file=args.verdict,
        date_str=args.date,
        run_url=args.run_url,
        historical_file=args.historical,
        output_file=args.out
    )
    
    # Imprimir resumen
    print("\n" + "="*60)
    print("REPORTE GENERADO")
    print("="*60)
    print(report_content[:500] + "...\n")


if __name__ == "__main__":
    main()
