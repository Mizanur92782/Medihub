import json
from django.http import HttpResponse
from django.shortcuts import render
from celery.app.control import Control
from medihub.celery import app as celery_app
from medihub.tasks import rabbitMQ_tester


def TeshMessageQuee(request):
    rabbitMQ_tester.delay()
    return HttpResponse("Task added to RabbitMQ message queue")


def _get_rabbitmq_queue_count():
    try:
        with celery_app.connection_or_acquire() as conn:
            with conn.channel() as channel:
                name, count, _ = channel.queue_declare(queue="celery", passive=True)
                return count
    except Exception:
        return "?"


def queue_dashboard(request):
    control = Control(celery_app)
    inspect = control.inspect(timeout=2)

    # Active tasks (being processed right now)
    active_raw = inspect.active() or {}
    active_tasks = []
    for worker, tasks in active_raw.items():
        for task in tasks:
            active_tasks.append({
                "worker": worker,
                "id": task.get("id"),
                "name": task.get("name"),
                "args": json.dumps(task.get("args", [])),
                "kwargs": json.dumps(task.get("kwargs", {})),
                "started": task.get("time_start"),
            })

    # Reserved tasks (fetched by worker, waiting to run)
    reserved_raw = inspect.reserved() or {}
    queued_tasks = []
    for worker, tasks in reserved_raw.items():
        for task in tasks:
            queued_tasks.append({
                "worker": worker,
                "id": task.get("id"),
                "name": task.get("name"),
                "args": json.dumps(task.get("args", [])),
                "kwargs": json.dumps(task.get("kwargs", {})),
            })

    # Registered task names per worker
    registered_raw = inspect.registered() or {}
    registered = [
        {"worker": worker, "tasks": tasks}
        for worker, tasks in registered_raw.items()
    ]

    # Worker stats
    stats_raw = inspect.stats() or {}
    workers = []
    for worker, stats in stats_raw.items():
        pool = stats.get("pool", {})
        total = stats.get("total", {})
        workers.append({
            "name": worker,
            "status": "Online",
            "concurrency": pool.get("max-concurrency", "?"),
            "processes": pool.get("processes", []),
            "completed": sum(total.values()) if total else 0,
        })

    if not workers:
        workers = [{"name": "No workers found", "status": "Offline", "concurrency": "-", "processes": [], "completed": 0}]

    context = {
        "active_tasks": active_tasks,
        "queued_tasks": queued_tasks,
        "registered": registered,
        "workers": workers,
        "active_count": len(active_tasks),
        "queued_count": len(queued_tasks),
        "worker_count": len(workers),
        "rabbitmq_queue_count": _get_rabbitmq_queue_count(),
    }
    return render(request, "queue_dashboard.html", context)
    