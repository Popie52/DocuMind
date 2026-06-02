from collections import defaultdict, deque

metrics = defaultdict(int)
response_times = deque(maxlen=1000)
rerank_times = deque(maxlen=1000)
def add_rerank_time(milliseconds: float):
    rerank_times.append(milliseconds)


def increment(metric_name: str):
    metrics[metric_name] += 1


def add_response_time(milliseconds: float):
    response_times.append(milliseconds)


def get_metrics():
    avg_response_time = (
        sum(response_times) / len(response_times)
        if response_times
        else 0
    )

    avg_rerank_time = (
        sum(rerank_times) / len(rerank_times)
        if rerank_times
        else 0
    )

    return {
        "questions_total": metrics["questions_total"],
        "semantic_queries_total": metrics["semantic_queries_total"],
        "page_queries_total": metrics["page_queries_total"],
        "failed_queries_total": metrics["failed_queries_total"],
        "avg_response_time_ms": round(avg_response_time, 2),
        "avg_rerank_time_ms": round(avg_rerank_time, 2),
    }


def reset_metrics():
    metrics.clear()
    response_times.clear()