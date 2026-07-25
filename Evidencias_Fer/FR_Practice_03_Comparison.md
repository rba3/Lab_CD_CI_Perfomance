📈 Comparación de Métricas Práctica 03
| Metric |	Run 30136393864 |	Run 30136717108 |	Difference	Trend |
| --- | --- | --- | --- |
| Threads (Concurrent Users) |	~40 threads |	~49 threads |	+9 threads (+22.5%)	📈 Increased |
| P95 Latency |	12.0 ms |	23.0 ms |	+11.0 ms (+91.7%)	📈 Degraded |
| Throughput |	51.06 req/s |	49.47 req/s |	-1.59 req/s (-3.1%)	📉 Decreased |

Conclusiones

- El cambio en parámetros subió la carga de peticiones lo cual incrementó el P95.
- El throughput baja debido al incremento de think time en el segundo escenario.
- Parece que los reportes tienen información del pico alcanzado de conexiones pero no el pico de conexiones esperadas en parámetros (se programaron con 55 y 80 conexiones).
