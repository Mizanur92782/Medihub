# System Architecture

```
─────────────────────────────────────────────────────────────────────┐
│                         INTERNET / BROWSER                          │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ :8080
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        NGINX (Load Balancer)                        │
│                         port: 8080                                  │
└──────────┬──────────────┬──────────────┬────────────────────────────┘
           │              │              │
           ▼              ▼              ▼
      ┌─────────┐   ┌─────────┐   ┌─────────┐
      │  web1   │   │  web2   │   │  web3   │
      │ :8011   │   │ :8012   │   │ :8013   │
      │gunicorn │   │gunicorn │   │gunicorn │
      │ Django  │   │ Django  │   │ Django  │
      └────┬────┘   └────┬────┘   └────┬────┘
           │              │              │
           └──────────────┼──────────────┘
                          │
           ┌──────────────┼──────────────┐
           ▼              ▼              ▼
      ┌─────────┐   ┌─────────┐   ┌──────────────┐
      │Postgres │   │  Redis  │   │  RabbitMQ    │
      │  :5432  │   │  :6379  │   │  :5672/15672 │
      └─────────┘   └─────────┘   └──────┬───────┘
                                          │
                              ┌───────────┴──────────┐
                              ▼                      ▼
                        ┌──────────┐         ┌────────────┐
                        │  Celery  │         │  Celery    │
                        │  Worker  │         │   Beat     │
                        └──────────┘         └────────────┘
```

---

## Monitoring Stack

```
  ┌──────────┐   ┌──────────┐   ┌─────────────┐   ┌─────────────┐
  │  web1    │   │ cAdvisor │   │    Node     │   │  Promtail   │
  │  web2    │──▶│  :8081   │   │  Exporter   │   │             │
  │  web3    │   │container │   │   :9100     │   │ reads docker│
  │ /metrics │   │ metrics  │   │host metrics │   │    logs     │
  └────┬─────┘   └────┬─────┘   └──────┬──────┘   └──────┬──────┘
       │              │                │                  │
       └──────────────┴────────────────┘                  │
                          │ scrape                        │ push
                          ▼                               ▼
                  ┌───────────────┐               ┌───────────────┐
                  │  Prometheus   │               │     Loki      │
                  │    :9090      │               │    :3100      │
                  │ stores metrics│               │ stores logs   │
                  └───────┬───────┘               └───────┬───────┘
                          │                               │
                          │ alerts                        │
                          ▼                               │
                  ┌───────────────┐                       │
                  │ Alertmanager  │                       │
                  │    :9093      │                       │
                  └───────┬───────┘                       │
                          │                               │
               ┌──────────┴──────────┐                   │
               ▼                     ▼                   │
        ┌────────────┐      ┌──────────────┐             │
        │   Email    │      │   Telegram   │             │
        │  (Gmail)   │      │     Bot      │             │
        └────────────┘      └──────────────┘             │
                                                         │
                          ┌──────────────────────────────┘
                          ▼
                  ┌───────────────┐
                  │    Grafana    │
                  │    :3000      │
                  │  Dashboard    │
                  │ Prometheus ───┤ metrics charts
                  │ Loki      ────┤ log viewer
                  └───────────────┘
```

---

## Dev Tools

```
  ┌──────────┐   ┌──────────┐   ┌──────────┐
  │ pgAdmin  │   │  Jaeger  │   │ RabbitMQ │
  │  :5050   │   │  :16686  │   │  :15672  │
  │ DB UI    │   │ Tracing  │   │Queue UI  │
  └──────────┘   └──────────┘   └──────────┘
```

---

## সার্ভিস পরিচিতি

| Service       | কাজ                                                              |
|---------------|------------------------------------------------------------------|
| Nginx         | সব request receive করে web1/2/3 এ ভাগ করে                       |
| Prometheus    | সব service থেকে metrics collect করে                              |
| cAdvisor      | প্রতিটা container এর resource usage collect করে                  |
| Node Exporter | পুরো server এর resource usage collect করে                        |
| Alertmanager  | Prometheus এর alert receive করে Email/Telegram পাঠায়             |
| Loki          | সব container এর logs store করে                                   |
| Promtail      | Docker logs পড়ে Loki তে পাঠায়                                   |
| Grafana       | Prometheus + Loki এর data সুন্দর dashboard এ দেখায়              |
