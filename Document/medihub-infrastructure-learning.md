# MediHub Infrastructure — সম্পূর্ণ শিক্ষামূলক গাইড
### Docker Compose, Monitoring এবং Logging Stack বাংলায়

---

> **এই ডকুমেন্টটি কার জন্য?**
> যারা MediHub প্রজেক্টের infrastructure বুঝতে চান — কোন service কী কাজ করে, কীভাবে একটি service আরেকটির সাথে যুক্ত, এবং কীভাবে data collect, store এবং visualize করা হয় — তাদের জন্য এই সম্পূর্ণ বাংলা গাইড।

---

## 📋 সূচিপত্র

1. [সম্পূর্ণ Architecture Overview](#architecture)
2. [Application Layer](#application-layer)
   - [Nginx](#nginx)
   - [Web1, Web2, Web3 (Django)](#django-web-servers)
   - [PostgreSQL](#postgresql)
   - [Redis](#redis)
3. [Background Task Layer](#background-tasks)
   - [RabbitMQ](#rabbitmq)
   - [Celery Worker](#celery-worker)
   - [Celery Beat](#celery-beat)
4. [Monitoring Stack](#monitoring-stack)
   - [Prometheus](#prometheus)
   - [Alertmanager](#alertmanager)
   - [Alerts Configuration](#alerts)
5. [Logging Stack](#logging-stack)
   - [Loki](#loki)
   - [Promtail](#promtail)
6. [Visualization ও Tracing](#visualization-tracing)
   - [Grafana](#grafana)
   - [Jaeger](#jaeger)
7. [Development Tools](#dev-tools)
   - [PgAdmin](#pgadmin)
8. [Service Relationship Map](#service-map)
9. [Data Flow — কীভাবে Data যায়](#data-flow)
10. [Configuration Files — বিস্তারিত ব্যাখ্যা](#config-files)

---

<a name="architecture"></a>
## 🏗️ ১. সম্পূর্ণ Architecture Overview

MediHub একটি **healthcare web application** যেটি চালানো হয় Docker Compose দিয়ে। মোট তিনটি বড় layer আছে:

```
┌─────────────────────────────────────────────────────┐
│                    INTERNET / USER                   │
└──────────────────────┬──────────────────────────────┘
                       │  Port 8080
┌──────────────────────▼──────────────────────────────┐
│                  NGINX (Load Balancer)               │
└────────┬─────────────┬─────────────┬────────────────┘
         │             │             │
    Port 8011     Port 8012     Port 8013
┌────────▼──┐  ┌───────▼──┐  ┌──────▼───┐
│  Django   │  │  Django  │  │  Django  │
│  Web 1    │  │  Web 2   │  │  Web 3   │
└─────┬─────┘  └────┬─────┘  └────┬─────┘
      │              │              │
      └──────────────┼──────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐   ┌─────────▼────────┐
│  PostgreSQL DB  │   │     Redis Cache  │
└─────────────────┘   └──────────────────┘

BACKGROUND TASKS:
RabbitMQ → Celery Worker (task execute)
           Celery Beat   (scheduled tasks)

MONITORING:
Prometheus ← scrapes metrics from Web1, Web2, Web3
Prometheus → triggers alerts → Alertmanager → Email

LOGGING:
Promtail ← Docker container logs
Promtail → pushes to → Loki

VISUALIZATION:
Grafana ← reads from Prometheus + Loki
Jaeger  ← receives traces from Django apps
```

---

<a name="application-layer"></a>
## 🌐 ২. Application Layer

<a name="nginx"></a>
### 2.1 Nginx — Load Balancer ও Reverse Proxy

**Nginx কী?**
Nginx একটি high-performance web server যেটি এখানে **reverse proxy** এবং **load balancer** হিসেবে কাজ করছে। মানে হলো — user যখন browser থেকে request পাঠায়, সেটি সরাসরি Django-তে যায় না। আগে Nginx-এ আসে, তারপর Nginx সেটিকে ৩টি Django server-এর মধ্যে ভাগ করে দেয়।

**কেন Nginx ব্যবহার করা হয়?**
- একটিমাত্র port (8080) দিয়ে সব traffic handle করা যায়
- ৩টি Django instance-এ load distribute করে — একটি heavy হলে অন্যগুলো নেয়
- Static files (CSS, JS, images) নিজেই serve করে, Django-কে বিরক্ত করে না
- SSL/TLS termination করতে পারে

**Docker Compose Configuration:**
```yaml
nginx:
  image: nginx:alpine
  container_name: medihub_nginx
  ports:
    - "8080:80"          # Host এর 8080 port → Container এর 80 port
  volumes:
    - ../nginx/nginx.conf:/etc/nginx/nginx.conf:ro   # Config file mount (read-only)
    - static_volume:/app/staticfiles                  # Django static files
    - media_volume:/app/media                         # User uploaded files
  depends_on:
    web1:
      condition: service_healthy    # web1 healthy না হলে start হবে না
    web2:
      condition: service_healthy
    web3:
      condition: service_healthy
  deploy:
    resources:
      limits:
        cpus: "0.5"       # সর্বোচ্চ CPU: অর্ধেক core
        memory: 256M      # সর্বোচ্চ RAM: 256 MB
```

**কীভাবে কাজ করে:**
1. User → `http://your-server:8080` request করে
2. Nginx সেটি পায়, `nginx.conf` দেখে কোন upstream-এ পাঠাবে
3. Round-robin বা অন্য algorithm-এ web1/web2/web3-এ forward করে
4. Static files request হলে সরাসরি volume থেকে serve করে

---

<a name="django-web-servers"></a>
### 2.2 Web1, Web2, Web3 — Django Application Servers

**তিনটি Django Server কেন?**
এটাকে বলে **horizontal scaling**। একটি server যদি অনেক বেশি request পায়, সেটি slow হয়ে যায়। তাই একই application ৩ জায়গায় চালানো হয় — load ভাগ হয়ে যায়।

**প্রতিটি Server-এর Configuration:**

```yaml
web1:
  image: medihub_web          # একই Docker image, তিনটিতেই
  container_name: medihub_web1
  hostname: medihub_web1       # Container এর নাম, Prometheus এটি দিয়ে চেনে
  env_file:
    - ../.env                  # Secret keys, DB passwords এখানে
  environment:
    - PORT=8011                # web1 চলে port 8011-এ
  ports:
    - "8011:8011"
  volumes:
    - ..:/app                  # Code mount করা হয়েছে
    - static_volume:/app/staticfiles
    - media_volume:/app/media
  depends_on:
    db:
      condition: service_healthy       # DB ready না হলে শুরু হবে না
    redis:
      condition: service_healthy
    migrate:
      condition: service_completed_successfully  # Migration শেষ হলেই শুরু
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8011/health/"]
    interval: 30s      # প্রতি ৩০ সেকেন্ডে health check
    timeout: 10s       # ১০ সেকেন্ডের মধ্যে response না এলে fail
    retries: 3         # ৩ বার fail হলে unhealthy
    start_period: 40s  # শুরুতে ৪০ সেকেন্ড grace time
  deploy:
    resources:
      limits:
        cpus: "1"
        memory: 512M
```

> **web2 এবং web3** একই configuration — শুধু port আলাদা (8012, 8013)।

**`/health/` endpoint কী?**
Django application-এ একটি simple view যেটি শুধু `HTTP 200 OK` response দেয়। Docker এটি দিয়ে বোঝে server live আছে কিনা। যদি না থাকে, Docker container restart করে।

**`migrate` service কী করে?**
```yaml
migrate:
  command:
    - "chown -R app:app /app/staticfiles"      # File permission ঠিক করে
    - "python manage.py migrate --fake-initial" # Database tables তৈরি করে
    - "python manage.py collectstatic --noinput" # Static files একজায়গায় আনে
```
এটি একবার চলে এবং বন্ধ হয়ে যায় (`restart: no`)। Web servers এটি শেষ হওয়ার জন্য অপেক্ষা করে।

---

<a name="postgresql"></a>
### 2.3 PostgreSQL — Primary Database

**PostgreSQL কী?**
এটি একটি open-source relational database। MediHub-এর সব data (users, appointments, medical records, ইত্যাদি) এখানে stored থাকে।

```yaml
db:
  image: postgres:16-alpine     # Alpine = ছোট size এর Linux
  container_name: medihub_db
  env_file:
    - ../.env                   # POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB এখানে
  volumes:
    - db_data:/var/lib/postgresql/data   # Data persist করার জন্য named volume
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U $$POSTGRES_USER -d $$POSTGRES_DB"]
    # pg_isready = PostgreSQL-এর built-in health check tool
    interval: 10s
    timeout: 5s
    retries: 5
  deploy:
    resources:
      limits:
        cpus: "1"
        memory: 512M
```

**`db_data` volume কেন?**
Docker container বন্ধ হলে সব data হারিয়ে যায়। `db_data` volume ব্যবহার করলে container বন্ধ করলেও data থাকে। এটি host machine-এ `/var/lib/docker/volumes/db_data/` তে stored থাকে।

**`$$POSTGRES_USER` — `$$` কেন?**
Docker Compose-এ `$` দিয়ে environment variable পড়া হয়। কিন্তু PostgreSQL healthcheck command shell-এর ভেতরে চলে, তাই shell variable বোঝাতে `$$` লিখতে হয় — Docker যেন আগে substitute না করে।

---

<a name="redis"></a>
### 2.4 Redis — Cache এবং Session Storage

**Redis কী?**
Redis একটি in-memory data store। এটি অনেক দ্রুত কারণ data RAM-এ থাকে, disk-এ না। MediHub ব্যবহার করে:
- **Caching** — বারবার same DB query না করে Redis-এ result রাখা
- **Session storage** — user login session
- **Celery broker** (optional) — task queue হিসেবেও কাজ করতে পারে

```yaml
redis:
  image: redis:7-alpine
  container_name: medihub_redis
  command: ["sh", "-c", "redis-server --requirepass $$REDIS_PASSWORD"]
  # Password দিয়ে Redis start করা হচ্ছে
  env_file:
    - ../.env                # REDIS_PASSWORD এখানে থাকে
  healthcheck:
    test: ["CMD-SHELL", "redis-cli -a $$REDIS_PASSWORD ping"]
    # redis-cli ping → PONG আসলে healthy
    interval: 10s
    timeout: 5s
    retries: 5
  deploy:
    resources:
      limits:
        cpus: "0.5"
        memory: 256M
```

**Password কেন দরকার?**
Default-এ Redis কোনো authentication ছাড়াই accessible। Production-এ এটি বিপজ্জনক। `--requirepass` দিয়ে password set করা হলে যেকোনো connection-এ password দিতে হবে।

---

<a name="background-tasks"></a>
## ⚙️ ৩. Background Task Layer

<a name="rabbitmq"></a>
### 3.1 RabbitMQ — Message Broker

**RabbitMQ কী?**
RabbitMQ একটি **message broker** বা **message queue**। এটি tasks-এর একটি "waiting room" এর মতো। Django যখন কোনো heavy task করতে চায় (যেমন: email পাঠানো, report generate করা), সেটি সরাসরি না করে RabbitMQ-তে একটি "message" রাখে। Celery Worker পরে সেটি তুলে নিয়ে কাজ করে।

**কেন এটি দরকার?**
User যদি email পাঠানোর request করে, email send হতে ৩-৪ সেকেন্ড লাগতে পারে। এই সময় user কে wait করালে experience খারাপ হয়। RabbitMQ দিয়ে task background-এ চলে, user instant response পায়।

```yaml
rabbitmq:
  image: rabbitmq:3-management-alpine
  # "management" version = web UI সহ
  container_name: medihub_rabbitmq
  ports:
    - "5672:5672"    # AMQP protocol port (application এর জন্য)
    - "15672:15672"  # Management web UI port
  environment:
    - RABBITMQ_DEFAULT_USER=medihub
    - RABBITMQ_DEFAULT_PASS=medihub
  volumes:
    - rabbitmq_data:/var/lib/rabbitmq   # Queue data persist
  healthcheck:
    test: ["CMD", "rabbitmq-diagnostics", "ping"]
    interval: 10s
    timeout: 5s
    retries: 5
```

**Management UI:**
`http://your-server:15672` এ গেলে RabbitMQ-এর web dashboard দেখা যায়। সেখানে কতগুলো message queue-তে আছে, কতগুলো process হচ্ছে সব দেখা যায়।

---

<a name="celery-worker"></a>
### 3.2 Celery Worker — Background Task Executor

**Celery Worker কী?**
Celery Worker একটি process যেটি RabbitMQ-এর queue থেকে tasks নিয়ে execute করে। একাধিক worker চালালে parallel-এ অনেক task হয়।

```yaml
celery_worker:
  image: medihub_web           # Django app এর same image
  container_name: medihub_celery_worker
  command: celery -A medihub worker --loglevel=info
  # celery -A medihub = medihub project এর celery app ব্যবহার কর
  # worker = worker mode-এ চালাও
  # --loglevel=info = info level log দেখাও
  env_file:
    - ../.env
  volumes:
    - ..:/app
  depends_on:
    rabbitmq:
      condition: service_healthy
    redis:
      condition: service_healthy
    migrate:
      condition: service_completed_successfully
  restart: always
  deploy:
    resources:
      limits:
        cpus: "1"
        memory: 512M
```

**কীভাবে কাজ করে:**
```
Django App → task.delay() → RabbitMQ queue
                                    ↓
                            Celery Worker polls
                                    ↓
                            Task execute করে
                                    ↓
                            Result Redis-এ store করে (optional)
```

---

<a name="celery-beat"></a>
### 3.3 Celery Beat — Scheduled Task Scheduler

**Celery Beat কী?**
Celery Beat একটি **scheduler** — এটি cron job-এর মতো কাজ করে। নির্দিষ্ট সময়ে নির্দিষ্ট tasks automatically queue-তে দেয়।

উদাহরণ:
- প্রতিদিন রাত ১২টায় appointment reminder email পাঠানো
- প্রতি ঘণ্টায় database cleanup
- প্রতি সপ্তাহে analytics report generate করা

```yaml
celery_beat:
  image: medihub_web
  container_name: medihub_celery_beat
  command: celery -A medihub beat --loglevel=info
  # beat = scheduler mode
  env_file:
    - ../.env
  volumes:
    - ..:/app
  depends_on:
    rabbitmq:
      condition: service_healthy
    migrate:
      condition: service_completed_successfully
  restart: always
```

> ⚠️ **গুরুত্বপূর্ণ:** Celery Beat সবসময় **একটিমাত্র** instance চালাতে হবে। দুটো চালালে same task দুইবার execute হবে।

---

<a name="monitoring-stack"></a>
## 📊 ৪. Monitoring Stack

<a name="prometheus"></a>
### 4.1 Prometheus — Metrics Collection ও Storage

**Prometheus কী?**
Prometheus একটি **time-series database** এবং **monitoring system**। এটি নিয়মিত বিভিন্ন service থেকে metrics (সংখ্যা-ভিত্তিক তথ্য) collect করে এবং store করে।

**Metrics কী?**
Metrics হলো সংখ্যা-ভিত্তিক performance data। যেমন:
- কতটা CPU ব্যবহার হচ্ছে
- কতটি HTTP request এলো
- Response time কত millisecond
- কতজন user active আছে

**"Pull" model:**
Prometheus নিজে গিয়ে services থেকে data নিয়ে আসে (pull করে)। Services Prometheus-এর জন্য অপেক্ষা করে না।

```yaml
prometheus:
  image: prom/prometheus:latest
  container_name: medihub_prometheus
  ports:
    - "9090:9090"     # Prometheus web UI ও API
  volumes:
    - ../monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
    - ../monitoring/alerts.yml:/etc/prometheus/alerts.yml:ro
    - prometheus_data:/prometheus    # Metrics data persist
  command: --config.file=/etc/prometheus/prometheus.yml
  restart: always
  networks:
    - app_network
```

**`prometheus_data` volume কেন?**
Prometheus-এর metrics হলো historical data। Container restart হলেও যেন পুরনো data না যায়, তাই volume ব্যবহার করা হয়।

---

#### `prometheus.yml` — বিস্তারিত Configuration ব্যাখ্যা

```yaml
global:
  scrape_interval: 15s   # প্রতি ১৫ সেকেন্ডে metrics collect করবে

alerting:
  alertmanagers:
    - static_configs:
        - targets: ["alertmanager:9093"]
        # Prometheus alert fire হলে এই address-এ পাঠাবে

rule_files:
  - /etc/prometheus/alerts.yml
  # Alert rules কোথায় আছে

scrape_configs:
  # কোন কোন service থেকে metrics নেবে

  - job_name: medihub_web1         # এই job-এর নাম
    static_configs:
      - targets: ["medihub_web1:8011"]   # এই address-এ যাবে
    metrics_path: /metrics/              # এই endpoint-এ metrics পাবে

  - job_name: medihub_web2
    static_configs:
      - targets: ["medihub_web2:8012"]
    metrics_path: /metrics/

  - job_name: medihub_web3
    static_configs:
      - targets: ["medihub_web3:8013"]
    metrics_path: /metrics/
```

**কীভাবে কাজ করে:**
```
প্রতি ১৫ সেকেন্ডে:
Prometheus → HTTP GET medihub_web1:8011/metrics/ → Metrics পড়ে → Database-এ store করে
Prometheus → HTTP GET medihub_web2:8012/metrics/ → Metrics পড়ে → Database-এ store করে
Prometheus → HTTP GET medihub_web3:8013/metrics/ → Metrics পড়ে → Database-এ store করে
```

**Django কীভাবে `/metrics/` provide করে?**
Django app-এ `django-prometheus` library install থাকলে এই endpoint automatically তৈরি হয়। এটি অনেক built-in metrics expose করে যেমন:
- `django_http_requests_total` — মোট কতটি request এসেছে
- `django_http_requests_latency_seconds` — response time
- `django_db_execute_total` — database query count

---

<a name="alertmanager"></a>
### 4.2 Alertmanager — Alert Management ও Notification

**Alertmanager কী?**
Prometheus alert detect করলে Alertmanager সেটি handle করে। এটি alert গুলো **group** করে, **deduplicate** করে এবং **notify** করে (email, Slack, PagerDuty ইত্যাদিতে)।

```yaml
alertmanager:
  image: prom/alertmanager:latest
  container_name: medihub_alertmanager
  ports:
    - "9093:9093"
  volumes:
    - ../monitoring/alertmanager.yml:/etc/alertmanager/alertmanager.yml:ro
  command: --config.file=/etc/alertmanager/alertmanager.yml
  restart: always
  networks:
    - app_network
```

---

#### `alertmanager.yml` — বিস্তারিত Configuration ব্যাখ্যা

```yaml
global:
  smtp_smarthost: "smtp.gmail.com:587"
  # Gmail-এর SMTP server address ও port
  # Port 587 = TLS encryption সহ

  smtp_from: "medihub@gmail.com"
  # "From" address — email কোথা থেকে আসবে

  smtp_auth_username: "medihub@gmail.com"
  # Gmail login username

  smtp_auth_password: "your-app-password"
  # Gmail App Password (regular password না, 16-digit app password)
  # Gmail → Settings → Security → 2FA → App Passwords থেকে পাবেন

route:
  receiver: email_alert
  # সব alert এই receiver-এ যাবে

receivers:
  - name: email_alert
    email_configs:
      - to: "nightliver000@gmail.com"
        # Alert কোথায় পাঠাবে
        send_resolved: true
        # Alert resolve হলেও email পাঠাবে (যেমন: "Service is back up")
```

**Gmail App Password কেন?**
Google 2FA enable থাকলে regular password দিয়ে SMTP কাজ করে না। App Password হলো Google-এর দেওয়া special password যেটি শুধু third-party apps-এর জন্য।

**Alert Flow:**
```
Prometheus detects alert condition
        ↓
Prometheus → fires alert → Alertmanager (port 9093)
        ↓
Alertmanager groups + deduplicates alerts
        ↓
Alertmanager → sends email via Gmail SMTP
        ↓
nightliver000@gmail.com এ email পৌঁছায়
```

---

<a name="alerts"></a>
### 4.3 Alerts Configuration — কখন Alert হবে

#### `alerts.yml` — বিস্তারিত ব্যাখ্যা

```yaml
groups:
  - name: medihub_alerts      # Alert group এর নাম
    rules:

      # Alert 1: Service Down
      - alert: ServiceDown     # Alert এর নাম
        expr: up == 0          # PromQL expression: "up" metric 0 হলে
        # "up" metric Prometheus নিজেই set করে
        # scrape successful হলে up=1, fail হলে up=0
        for: 1m                # ১ মিনিট ধরে এই condition থাকলে alert fire হবে
        # এটি false positive এড়ায় — momentary blip alert না করে
        labels:
          severity: critical   # Alert এর গুরুত্ব level
        annotations:
          summary: "Service {{ $labels.job }} is down"
          # {{ $labels.job }} = কোন job down সেটি automatically আসবে
          # উদাহরণ: "Service medihub_web1 is down"

      # Alert 2: High Response Time
      - alert: HighResponseTime
        expr: django_http_requests_latency_seconds_by_view_method_sum > 2
        # Django-এর response time metric ২ সেকেন্ডের বেশি হলে
        for: 2m                # ২ মিনিট ধরে slow হলে alert
        labels:
          severity: warning    # Warning level (critical এর চেয়ে কম গুরুত্বপূর্ণ)
        annotations:
          summary: "High response time on {{ $labels.view }}"
          # {{ $labels.view }} = কোন view/endpoint slow সেটি দেখাবে
```

**Severity Levels:**
- `critical` → Service down, data loss সম্ভব — তাৎক্ষণিক action দরকার
- `warning` → Performance degraded — attention দরকার কিন্তু এখনি crisis না

**PromQL (Prometheus Query Language):**
Prometheus-এর নিজস্ব query language। কিছু উদাহরণ:
```
up == 0                          → যেসব service down
rate(http_requests_total[5m])    → প্রতি সেকেন্ডে request rate (৫ মিনিটের গড়)
memory_usage_bytes > 400000000   → ৪০০ MB-এর বেশি memory ব্যবহার
```

---

<a name="logging-stack"></a>
## 📝 ৫. Logging Stack

<a name="loki"></a>
### 5.1 Loki — Log Storage

**Loki কী?**
Loki হলো Grafana Labs-এর তৈরি **log aggregation system**। এটি Prometheus-এর মতো, কিন্তু metrics-এর বদলে **logs** store করে।

Loki-কে বলা হয় "Prometheus, but for logs"।

**Loki কেন Prometheus-এর চেয়ে আলাদা?**
- Prometheus: সংখ্যা (CPU: 45%, requests: 1000/s)
- Loki: text logs (`[ERROR] Database connection failed at 14:32:01`)

```yaml
loki:
  image: grafana/loki:2.9.0
  container_name: medihub_loki
  ports:
    - "3100:3100"     # Loki API port
  command: -config.file=/etc/loki/local-config.yaml
  # Default config ব্যবহার করছে
  restart: always
  networks:
    - app_network
```

**Loki কীভাবে কাজ করে?**
Loki নিজে logs collect করে না। Promtail (log shipper) logs পাঠায়, Loki সেগুলো index করে store করে। Grafana পরে Loki থেকে logs query করে দেখায়।

---

<a name="promtail"></a>
### 5.2 Promtail — Log Collector ও Shipper

**Promtail কী?**
Promtail একটি **log agent** যেটি Docker container-গুলোর logs পড়ে এবং Loki-তে push করে।

```yaml
promtail:
  image: grafana/promtail:2.9.0
  container_name: medihub_promtail
  volumes:
    - /var/lib/docker/containers:/var/lib/docker/containers:ro
    # সব Docker container-এর log files এখানে থাকে
    # :ro = read-only (শুধু পড়বে, লিখবে না)

    - /var/run/docker.sock:/var/run/docker.sock
    # Docker socket — এটি দিয়ে Docker-এর সাথে কথা বলে
    # Container info জানতে (name, labels)

    - ../monitoring/promtail.yml:/etc/promtail/config.yml
    # Promtail এর config file
  command: -config.file=/etc/promtail/config.yml
  depends_on:
    - loki    # Loki চালু না হলে start হবে না
  restart: always
  networks:
    - app_network
```

---

#### `promtail.yml` — বিস্তারিত Configuration ব্যাখ্যা

```yaml
server:
  http_listen_port: 9080    # Promtail এর নিজের HTTP port (status/metrics এর জন্য)
  grpc_listen_port: 0       # gRPC disabled (0 মানে random port, কিন্তু use হয় না)

positions:
  filename: /tmp/positions.yaml
  # Promtail কোন file কতটুকু পড়েছে সেটি এখানে save করে
  # Container restart হলেও সে জানে কোথা থেকে শুরু করতে হবে
  # এটি না থাকলে restart-এ same log দুইবার পাঠাত

clients:
  - url: http://loki:3100/loki/api/v1/push
  # Logs এই URL-এ push করবে
  # "loki" = Docker network-এর service name (DNS resolution)

scrape_configs:
  - job_name: medihub          # এই scrape job এর নাম

    docker_sd_configs:
      # "sd" = Service Discovery
      # Docker-এর মাধ্যমে container আবিষ্কার করে
      - host: unix:///var/run/docker.sock    # Docker daemon এর socket
        refresh_interval: 5s                 # প্রতি ৫ সেকেন্ডে নতুন container খোঁজে
        filters:
          - name: name
            values: [medihub_web1, medihub_web2, medihub_web3, medihub_nginx]
            # শুধু এই ৪টি container-এর logs নেবে

    relabel_configs:
      # Relabeling = log-এর সাথে extra metadata জুড়ে দেওয়া

      - source_labels: [__meta_docker_container_name]
        target_label: container
        # Container এর নাম "container" label-এ রাখবে
        # উদাহরণ: container="medihub_web1"

      - source_labels: [__meta_docker_container_log_stream]
        target_label: stream
        # Log কোথা থেকে এলো: "stdout" নাকি "stderr"
        # উদাহরণ: stream="stderr" মানে error log
```

**Docker Service Discovery কীভাবে কাজ করে:**
```
Promtail → Docker socket-এ query করে → "medihub_web1 container এর log কোথায়?"
Docker → /var/lib/docker/containers/<id>/<id>-json.log বলে দেয়
Promtail → সেই file read করে → Loki-তে push করে
```

**Log Pipeline:**
```
Django app (web1/web2/web3) → stdout/stderr
        ↓
Docker সেটি capture করে → /var/lib/docker/containers/[id]/[id]-json.log
        ↓
Promtail সেই file read করে + container metadata যোগ করে
        ↓
HTTP POST → Loki (port 3100)
        ↓
Loki index করে store করে
        ↓
Grafana → LogQL query করে → দেখায়
```

---

<a name="visualization-tracing"></a>
## 📈 ৬. Visualization ও Tracing

<a name="grafana"></a>
### 6.1 Grafana — Unified Dashboard

**Grafana কী?**
Grafana একটি **data visualization platform**। এটি Prometheus এবং Loki উভয় থেকে data নিয়ে সুন্দর interactive dashboard তৈরি করতে পারে।

```yaml
grafana:
  image: grafana/grafana:latest
  container_name: medihub_grafana
  ports:
    - "3000:3000"       # Web UI port
  environment:
    - GF_SECURITY_ADMIN_USER=admin
    - GF_SECURITY_ADMIN_PASSWORD=medihub_grafana
    # Default admin credentials
  volumes:
    - grafana_data:/var/lib/grafana    # Dashboard, datasource config persist
  depends_on:
    - loki      # Loki চালু হওয়ার পর start হবে
  restart: always
  networks:
    - app_network
```

**Grafana-তে কী দেখা যায়?**

1. **Metrics Dashboard (Prometheus থেকে):**
   - ৩টি Django server-এর response time graph
   - Request per second
   - Error rate
   - CPU ও Memory usage

2. **Logs Explorer (Loki থেকে):**
   - Real-time container logs
   - Error log search
   - Log patterns

**Data Sources Setup:**
Grafana-তে প্রথমে data sources add করতে হয়:
- Prometheus: `http://prometheus:9090`
- Loki: `http://loki:3100`

তারপর এই data sources ব্যবহার করে dashboards তৈরি করা যায়।

---

<a name="jaeger"></a>
### 6.2 Jaeger — Distributed Tracing

**Jaeger কী?**
Jaeger একটি **distributed tracing system**। এটি একটি request-এর সম্পূর্ণ journey track করে — কোন service কতক্ষণ নিল, কোথায় bottleneck আছে।

**Distributed Tracing কেন দরকার?**
ধরুন একটি user request আসলো। এটি:
1. Nginx-এ গেল (2ms)
2. Django-তে গেল (15ms)
3. Database query করলো (150ms) ← এখানে slow!
4. Redis cache check করলো (2ms)
5. Response দিলো

Jaeger এই পুরো flow-টি দেখায়। কোথায় কত সময় গেল সেটি স্পষ্ট।

```yaml
jaeger:
  image: jaegertracing/all-in-one:latest
  container_name: medihub_jaeger
  ports:
    - "16686:16686"       # Jaeger web UI
    - "6831:6831/udp"     # UDP port — application এখানে traces পাঠায়
  environment:
    - COLLECTOR_ZIPKIN_HOST_PORT=9411
    # Zipkin-compatible traces ও accept করতে পারবে
  restart: always
  networks:
    - app_network
```

**কীভাবে Django traces পাঠায়?**
Django app-এ `opentelemetry` বা `jaeger-client` library install করে configure করলে প্রতিটি request-এর trace automatically Jaeger-এ যায়।

---

<a name="dev-tools"></a>
## 🛠️ ৭. Development Tools

<a name="pgadmin"></a>
### 7.1 PgAdmin — PostgreSQL Web Interface

**PgAdmin কী?**
PgAdmin হলো PostgreSQL-এর graphical web interface। এটি দিয়ে database visually manage করা যায় — tables দেখা, queries run করা, data export করা ইত্যাদি।

```yaml
pgadmin:
  image: dpage/pgadmin4:latest
  container_name: medihub_pgadmin
  ports:
    - "5050:80"       # http://your-server:5050 এ accessible
  environment:
    - PGADMIN_DEFAULT_EMAIL=admin@medihub.com
    - PGADMIN_DEFAULT_PASSWORD=medihub_pgadmin
  volumes:
    - pgadmin_data:/var/lib/pgadmin    # Server connections, preferences persist
  depends_on:
    - db
  restart: always
  networks:
    - app_network
```

> ⚠️ **Production এ সতর্কতা:** PgAdmin শুধু development এ ব্যবহার করুন। Production-এ port 5050 publicly expose করা উচিত না।

---

<a name="service-map"></a>
## 🗺️ ৮. Service Relationship Map

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTERNAL ACCESS                          │
│  :8080 (Nginx)  :3000 (Grafana)  :9090 (Prometheus)        │
│  :16686 (Jaeger)  :5050 (PgAdmin)  :15672 (RabbitMQ UI)    │
└─────────────────────────────────────────────────────────────┘

APPLICATION FLOW:
User → Nginx(:8080) → Web1(:8011) ─┐
                    → Web2(:8012) ─┼→ PostgreSQL(:5432)
                    → Web3(:8013) ─┘  Redis(:6379)

BACKGROUND TASKS:
Web1/2/3 → RabbitMQ(:5672) → Celery Worker
Celery Beat → RabbitMQ(:5672) → Celery Worker

MONITORING FLOW:
Prometheus(:9090) ←scrapes← Web1(:8011/metrics/)
                  ←scrapes← Web2(:8012/metrics/)
                  ←scrapes← Web3(:8013/metrics/)
Prometheus → fires alerts → Alertmanager(:9093) → Email

LOGGING FLOW:
Web1/2/3/Nginx → Docker logs
Promtail → reads Docker logs → pushes to → Loki(:3100)

VISUALIZATION:
Grafana(:3000) ←queries← Prometheus(:9090)  [metrics]
Grafana(:3000) ←queries← Loki(:3100)        [logs]

TRACING:
Web1/2/3 → sends traces → Jaeger(:6831/udp)
Developer → views traces → Jaeger UI(:16686)
```

---

<a name="data-flow"></a>
## 🔄 ৯. Data Flow — কীভাবে Data যায়

### 9.1 User Request Flow

```
1. Browser → http://your-server:8080
2. Nginx receives request
3. Nginx checks upstream servers (web1, web2, web3)
4. Selects least-loaded server (e.g., web2)
5. Forwards request to web2:8012
6. Django processes: auth → business logic → DB query
7. PostgreSQL returns data
8. Django returns response
9. Nginx forwards response to browser
10. Browser renders page
```

### 9.2 Metrics Collection Flow

```
1. Every 15 seconds, Prometheus wakes up
2. HTTP GET → web1:8011/metrics/ 
   Response: 
   django_http_requests_total{method="GET"} 1523
   django_http_requests_latency_seconds_sum 45.3
   ...
3. Prometheus stores this as time-series data
4. Prometheus evaluates alert rules
5. If "up == 0" for 1 minute → fires ServiceDown alert
6. Alert sent to Alertmanager:9093
7. Alertmanager sends email to nightliver000@gmail.com
```

### 9.3 Log Collection Flow

```
1. Django app prints: logger.error("Payment failed: timeout")
2. Docker captures this as JSON:
   {"log": "Payment failed: timeout\n", "stream": "stderr", "time": "..."}
3. Saved to: /var/lib/docker/containers/[id]/[id]-json.log
4. Promtail reads new lines from this file
5. Promtail adds labels: {container="medihub_web2", stream="stderr"}
6. HTTP POST to loki:3100/loki/api/v1/push
7. Loki stores with timestamp + labels
8. Developer opens Grafana → Explore → Loki
9. Queries: {container="medihub_web2"} |= "ERROR"
10. Grafana shows matching logs
```

### 9.4 Background Task Flow

```
1. Doctor books appointment in Django
2. Django calls: send_reminder_email.delay(appointment_id=123)
   [.delay() = async, don't wait]
3. Task message pushed to RabbitMQ queue
4. Django returns "Booking confirmed!" to user immediately
5. Celery Worker picks up message from queue
6. Executes: send_reminder_email(appointment_id=123)
7. Fetches appointment from DB
8. Sends email via SMTP
9. Task complete
```

---

<a name="config-files"></a>
## 📁 ১০. Configuration Files — সম্পূর্ণ ব্যাখ্যা

### 10.1 Docker Networks — `app_network`

```yaml
networks:
  app_network:
    driver: bridge
```

**Network কেন দরকার?**
Docker container গুলো default-এ isolated। একটি container আরেকটির সাথে কথা বলতে পারে না। `app_network` তৈরি করে সব service-কে এতে যুক্ত করলে তারা service name দিয়ে একে অপরকে reach করতে পারে।

উদাহরণ:
- `http://loki:3100` — এটি DNS resolution: Docker জানে "loki" নামের container-এর IP কোনটি
- `http://prometheus:9090`
- `postgresql://db:5432`

**Bridge network:** Host machine থেকে isolated একটি virtual network।

---

### 10.2 Volumes — Data Persistence

```yaml
volumes:
  db_data:           # PostgreSQL এর সব data
  static_volume:     # Django static files (CSS, JS, images)
  media_volume:      # User uploaded files
  grafana_data:      # Grafana dashboards, datasource config
  prometheus_data:   # Prometheus time-series database
  rabbitmq_data:     # RabbitMQ queue data
  pgadmin_data:      # PgAdmin server connections
```

**Named Volumes vs Bind Mounts:**

| Type | উদাহরণ | কখন ব্যবহার |
|------|---------|-------------|
| Named Volume | `db_data:/var/lib/postgresql/data` | Data persist করতে, Docker manage করে |
| Bind Mount | `../nginx/nginx.conf:/etc/nginx/nginx.conf` | Config files, Code — host থেকে directly |

---

### 10.3 Resource Limits — কেন দরকার?

```yaml
deploy:
  resources:
    limits:
      cpus: "1"
      memory: 512M
```

Resource limits ছাড়া একটি service সব CPU/RAM নিয়ে নিতে পারে, বাকিগুলো crash করে। এই limits দিয়ে নিশ্চিত করা যায় প্রতিটি service তার allocated resource-এর মধ্যে থাকে।

---

### 10.4 Depends_on ও Health Checks — Startup Order

```yaml
depends_on:
  db:
    condition: service_healthy    # db healthy হলে শুরু করো
  migrate:
    condition: service_completed_successfully  # migrate শেষ হলে শুরু করো
```

**কেন এটি দরকার?**
Docker Compose সব service একসাথে start করে। Django যদি DB ready হওয়ার আগে start করে, সে DB connect করতে পারবে না এবং crash করবে। `depends_on` এই problem সমাধান করে।

**Condition types:**
- `service_started` → container শুধু start হলেই (healthy কিনা জানে না)
- `service_healthy` → healthcheck pass করলে (safe)
- `service_completed_successfully` → container exit code 0 দিয়ে বন্ধ হলে (migrate-এর জন্য)

---

## 🔐 ১১. Security বিষয়গুলো

### Environment Variables (`.env` file)
```
# .env file এ থাকে:
POSTGRES_USER=medihub_user
POSTGRES_PASSWORD=strong_password_here
POSTGRES_DB=medihub_db
REDIS_PASSWORD=redis_password_here
SECRET_KEY=django_secret_key_here
```

`.env` file কখনো git-এ commit করবেন না। `.gitignore`-এ রাখুন।

### Default Passwords যেগুলো পরিবর্তন করতে হবে:
| Service | Config এ আছে | পরিবর্তন করুন |
|---------|--------------|----------------|
| RabbitMQ | `medihub/medihub` | হ্যাঁ |
| PgAdmin | `medihub_pgadmin` | হ্যাঁ |
| Grafana | `medihub_grafana` | হ্যাঁ |
| Alertmanager | Gmail app password | `.env`-এ রাখুন |

---

## 📌 ১২. Quick Reference — কোন Service কোন Port

| Service | Port | কী দেখা যায় |
|---------|------|-------------|
| Nginx | 8080 | Main application |
| Grafana | 3000 | Dashboards (metrics + logs) |
| Prometheus | 9090 | Raw metrics + query |
| Alertmanager | 9093 | Active alerts |
| Loki | 3100 | Log storage API |
| Jaeger | 16686 | Distributed traces |
| PgAdmin | 5050 | Database management |
| RabbitMQ UI | 15672 | Queue management |
| Django Web1 | 8011 | Direct (bypass Nginx) |
| Django Web2 | 8012 | Direct (bypass Nginx) |
| Django Web3 | 8013 | Direct (bypass Nginx) |

---

## 🎓 সারসংক্ষেপ

MediHub-এর infrastructure তিনটি মূল layer-এ বিভক্ত:

**Application Layer** — Nginx load balance করে ৩টি Django instance-এ, যেগুলো PostgreSQL-এ data রাখে এবং Redis-এ cache করে। Background-এ RabbitMQ ও Celery heavy tasks handle করে।

**Monitoring Layer** — Prometheus প্রতি ১৫ সেকেন্ডে সব Django instance থেকে metrics collect করে। কোনো issue হলে Alertmanager email পাঠায়। Jaeger individual request traces track করে।

**Logging Layer** — Promtail সব container-এর logs পড়ে Loki-তে পাঠায়। Grafana একটি unified interface-এ Prometheus-এর metrics এবং Loki-র logs একসাথে দেখায়।

এই তিনটি layer মিলে একটি production-ready, observable, এবং scalable system তৈরি করে।

---

*ডকুমেন্ট তৈরি: MediHub Infrastructure Team*
*Version: 1.0 | ভাষা: বাংলা*
