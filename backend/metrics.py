"""Custom Prometheus metrics for the RAG pipeline.

These register on the default prometheus_client registry, which is the same
one `prometheus-fastapi-instrumentator` exposes at /metrics. So importing this
module anywhere in the app is enough for the metrics to show up.

Metric naming follows Prometheus conventions:
- Counters end in `_total` and only ever go up.
- Histograms expose `_bucket`, `_sum` and `_count` series, which let you
  compute rates, averages and quantiles (e.g. p95 latency) in PromQL.
"""
from prometheus_client import Counter, Histogram

# How many RAG queries we have answered, and how many blew up.
RAG_QUERIES = Counter(
    "rag_queries_total", "Total RAG queries processed"
)
RAG_ERRORS = Counter(
    "rag_query_errors_total", "RAG queries that raised an error"
)

# Latency broken down by stage, so you can see WHERE the time goes:
# vector retrieval vs the OpenAI call vs the whole thing end to end.
RAG_LATENCY = Histogram(
    "rag_query_duration_seconds", "End-to-end RAG query latency (seconds)"
)
RAG_RETRIEVAL_LATENCY = Histogram(
    "rag_retrieval_duration_seconds", "Vector retrieval latency (seconds)"
)
RAG_LLM_LATENCY = Histogram(
    "rag_llm_duration_seconds", "OpenAI generation latency (seconds)"
)

# Distribution of the model's self-reported confidence (0..1).
RAG_CONFIDENCE = Histogram(
    "rag_answer_confidence",
    "Model-reported answer confidence",
    buckets=[0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
)
