# Dockerfile ও entrypoint.sh — বাংলায় বিস্তারিত ব্যাখ্যা

> প্রতিটি লাইন **কী করে**, **কেন ব্যবহার করা হয়**, **না ব্যবহার করলে কী সমস্যা হয়**, এবং **কোন দর্শন বা কৌশল** এর পেছনে কাজ করছে — সম্পূর্ণ বাংলায়।

---

## Part 1 — Dockerfile

---

### লাইন ১ — বেস ইমেজ

```dockerfile
FROM python:3.11-slim
```

**কী করে:**
Docker Hub থেকে অফিসিয়াল Python 3.11 এর `slim` ভার্সন ডাউনলোড করে। এটাই পুরো ইমেজের ভিত্তি — এর উপরে বাকি সব কিছু তৈরি হয়।

**কেন ব্যবহার করা হয়:**
- `python:3.11` দিলে Python ম্যানুয়ালি ইনস্টল করতে হয় না।
- `-slim` মানে ছোট ভার্সন — অপ্রয়োজনীয় ডকুমেন্টেশন, টেস্ট ফাইল, বিল্ড টুল বাদ দেওয়া হয়েছে।
- পূর্ণ ইমেজ (~900 MB) বনাম slim (~50 MB) — অনেক ছোট।

**না ব্যবহার করলে কী হয়:**
- ইমেজ প্রায় ১৮ গুণ বড় হয়ে যায়।
- ডাউনলোড, আপলোড, এবং মেমোরি সবই বেশি লাগে।
- ভুল Python ভার্সন দিলে dependency সমস্যা হয়।

**দর্শন — "শুধু যা দরকার তাই রাখো":**
> ছোট ইমেজ মানে কম নিরাপত্তা ঝুঁকি, দ্রুত CI/CD পাইপলাইন, এবং কম খরচ। `slim` হলো সেরা ব্যালেন্স।

---

### লাইন ৩–৪ — Python এনভায়রনমেন্ট ভেরিয়েবল

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
```

**কী করে:**

| ভেরিয়েবল | কাজ |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1` | Python কে `.pyc` (কম্পাইল করা) ফাইল তৈরি করতে নিষেধ করে |
| `PYTHONUNBUFFERED=1` | Python এর stdout/stderr কে সাথে সাথে flush করতে বাধ্য করে — কোনো buffer থাকে না |

**কেন ব্যবহার করা হয়:**
- Container ephemeral (অস্থায়ী) — প্রতিবার নতুন করে তৈরি হয়। তাই `.pyc` ফাইল রাখার কোনো মানে নেই, শুধু জায়গা নষ্ট।
- Unbuffered না হলে `docker logs` এ log দেরিতে আসে। Container crash করলে buffer এ থাকা সব log **চিরতরে হারিয়ে যায়**।

**না ব্যবহার করলে কী হয়:**
- `PYTHONDONTWRITEBYTECODE` ছাড়া: ইমেজে অকেজো `.pyc` ফাইল জমে।
- `PYTHONUNBUFFERED` ছাড়া: লগ দেখা যায় না, debug করা অনেক কঠিন হয়ে যায়।

**দর্শন — "লগ হবে সরাসরি stream":**
> Container এর লগ সবসময় stdout/stderr এ যাওয়া উচিত — যাতে Docker বা Kubernetes সেটা collect করতে পারে। Buffer এই নিয়ম ভাঙে।

---

### লাইন ৬ — কাজের ডিরেক্টরি

```dockerfile
WORKDIR /app
```

**কী করে:**
Container এর ভেতরে `/app` কে working directory হিসেবে সেট করে। পরের সব `RUN`, `COPY`, `ENTRYPOINT` এই ডিরেক্টরি থেকে চলে।

**কেন ব্যবহার করা হয়:**
- সব প্রজেক্ট ফাইল একটি পরিচিত জায়গায় থাকে।
- Root `/` এ কাজ করার বিপদ এড়ানো যায়।
- পরের COPY কমান্ডে শুধু `.` লিখলেই হয়, পুরো path লিখতে হয় না।

**না ব্যবহার করলে কী হয়:**
- সব কমান্ড root থেকে চলে — বিপজ্জনক এবং অগোছালো।
- প্রতিটি জায়গায় full path লিখতে হয়।

**দর্শন — "Convention over Configuration":**
> `/app` Docker দুনিয়ায় standard। যে কেউ প্রজেক্টে যোগ দিলেই বুঝতে পারবে ফাইল কোথায় আছে।

---

### লাইন ৮ — System Dependency ইনস্টল (প্রথমবার)

```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
```

**কী করে:**
১. `apt-get update` — package list আপডেট করে।
২. `apt-get install -y --no-install-recommends curl` — `curl` ইনস্টল করে, extra recommended package ছাড়া।
৩. `rm -rf /var/lib/apt/lists/*` — ডাউনলোড করা package index মুছে দেয়।

**কেন ব্যবহার করা হয়:**
- `curl` health check বা script download এর জন্য লাগে।
- `--no-install-recommends` দিলে apt অপ্রয়োজনীয় ১০–৫০ MB extra package আনে না।
- `rm -rf` না করলে package index (~৩০–৫০ MB) ইমেজে বাকি থাকে।

**না ব্যবহার করলে কী হয়:**
- `apt-get update` ছাড়া install করলে পুরানো বা unavailable package পাবে।
- `rm -rf` ছাড়া ইমেজ বড় হয়ে যায়।

**⚠️ গুরুত্বপূর্ণ — ডুপ্লিকেট সমস্যা (লাইন ৮ ও ১২):**
এই Dockerfile এ `curl` **দুইবার** ইনস্টল হচ্ছে — এটি একটি **bug বা ভুল**। দুটো `RUN` একসাথে মিলিয়ে দেওয়া উচিত।

**দর্শন — "Layer Caching ও Cleanup":**
> প্রতিটি `RUN` একটি নতুন layer তৈরি করে। cleanup (`rm -rf`) অবশ্যই **একই `RUN` কমান্ডে** করতে হবে — আলাদা `RUN` এ করলে আগের layer ছোট হয় না।

---

### লাইন ১০ — Non-Root User তৈরি

```dockerfile
RUN addgroup --system app && adduser --system --ingroup app app
```

**কী করে:**
১. `app` নামে একটি system group তৈরি করে।
২. `app` নামে একটি system user তৈরি করে যার কোনো home directory বা login shell নেই।

**কেন ব্যবহার করা হয়:**
Default এ Docker container **root (UID 0)** হিসেবে চলে। মানে যদি কেউ আপনার app এ attack করে, সে container এর ভেতরে root হয়ে যায় — এবং host machine এও প্রবেশ করতে পারে।

Non-root user ব্যবহারে:
- Attack এর ক্ষতি সীমিত থাকে।
- Kubernetes security policy pass হয়।
- Security scanner (Snyk, Trivy) এটাকে HIGH risk হিসেবে flag করে না।

**না ব্যবহার করলে কী হয়:**
- আপনার Django app root হিসেবে চলে।
- যেকোনো dependency vulnerability মানেই attacker এর হাতে full container root।

**দর্শন — "Least Privilege" (ন্যূনতম অধিকার):**
> একটি প্রক্রিয়ার শুধু যতটুকু permission দরকার ততটুকুই থাকা উচিত। Web app চালাতে root লাগে না — তাই root দেওয়া উচিত না।

---

### লাইন ১২ — curl আবার ইনস্টল (অপ্রয়োজনীয়)

```dockerfile
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
```

**কী করে:**
লাইন ৮ এর মতোই curl ইনস্টল করে, কিন্তু এবার `--no-install-recommends` ছাড়া।

**সমস্যা:**
এটি সম্পূর্ণ অপ্রয়োজনীয় — copy-paste ভুল। এটি একটি extra layer যোগ করে এবং আগের চেয়ে বেশি package ইনস্টল করতে পারে।

**সমাধান:** লাইন ৮ ও ১২ একত্রিত করুন বা একটি মুছে দিন।

---

### লাইন ১৪–১৫ — Python Dependency ইনস্টল

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt
```

**কী করে:**
১. শুধু `requirements.txt` কপি করে (source code এর আগে)।
২. pip আপগ্রেড করে।
৩. সব Python package ইনস্টল করে।
৪. `--no-cache-dir` — pip এর local cache সংরক্ষণ করে না।

**কেন `requirements.txt` আগে কপি করা হয়?**
এটি **Docker Layer Cache Optimization** কৌশল।

Docker প্রতিটি layer cache করে রাখে। যদি `requirements.txt` না বদলায়, Docker cached pip install layer ব্যবহার করে — পুরো install আবার করে না। এতে build সময় ৩০ সেকেন্ড থেকে কয়েক মিনিট বাঁচে।

যদি আগে `COPY . .` করতেন, তাহলে যেকোনো ছোট code change এও pip install আবার চলত।

**`--no-cache-dir` কেন?**
Container এ "পরের বার" বলে কিছু নেই — cache শুধু ইমেজের সাইজ বাড়ায়, কোনো কাজে আসে না।

**না ব্যবহার করলে কী হয়:**
- প্রতিটি code change এ full `pip install` — ৫ সেকেন্ডের build হয় ২ মিনিটের।
- `--no-cache-dir` ছাড়া ইমেজ ১০০+ MB বড় হয়ে যায়।

**দর্শন — "Cache-Friendly Layering":**
> Dockerfile এর instruction সাজাও "কম পরিবর্তনশীল থেকে বেশি পরিবর্তনশীল" ক্রমে। Base → System → Python Deps → Source Code।

---

### লাইন ১৭ — Source Code কপি

```dockerfile
COPY . .
```

**কী করে:**
প্রজেক্টের সব ফাইল host থেকে container এর `/app/` এ কপি করে।

**কেন সবার শেষে?**
Source code প্রতিটি commit এ বদলায়। শেষে রাখলে শুধু এই layer invalidate হয় — উপরের pip install layer এ হাত পড়ে না।

**সতর্কতা — `.dockerignore` জরুরি:**
`.dockerignore` ছাড়া এই কমান্ড `.git/`, `__pycache__/`, `.env` ফাইলও কপি করে — যা বিপজ্জনক এবং অপ্রয়োজনীয়।

**দর্শন — "Build Context Hygiene":**
> ইমেজে শুধু যা চালানোর জন্য দরকার তাই রাখো। secret ফাইল, editor config, local cache — এগুলো production image এ যাওয়া উচিত না।

---

### লাইন ১৯–২১ — Permission সেটআপ

```dockerfile
RUN chmod +x /app/Docker/entrypoint.sh && \
    mkdir -p /app/staticfiles /app/media /app/logs && \
    chown -R app:app /app
```

**কী করে:**
১. `chmod +x` — entrypoint script কে executable করে।
২. `mkdir -p` — staticfiles, media, logs ডিরেক্টরি তৈরি করে।
৩. `chown -R app:app /app` — পুরো `/app` ডিরেক্টরির মালিকানা `app` user কে দেয়।

**না ব্যবহার করলে কী হয়:**

| কমান্ড | না থাকলে |
|---|---|
| `chmod +x` | Container শুরুতেই `Permission denied` error দেয় |
| `mkdir -p staticfiles` | Django এর `collectstatic` fail করে |
| `chown -R app:app /app` | `app` user ফাইল পড়তে বা লিখতে পারে না |

**কেন একটি `RUN` এ?**
`&&` দিয়ে জুড়ে দেওয়া হয়েছে যাতে একটি layer এ সব হয় — layer কম মানে ইমেজ ছোট।

**দর্শন — "Fail Fast" (দ্রুত ব্যর্থ হওয়া):**
> Runtime এ রাত ২টায় permission error দেখার চেয়ে build time এ সমস্যা ধরা অনেক ভালো।

---

### লাইন ২৩ — Non-Root User সক্রিয় করা

```dockerfile
USER app
```

**কী করে:**
পরের সব instruction (`ENTRYPOINT`, `CMD`) `app` user হিসেবে চালানো হবে।

**কেন `chown` এর পরে?**
যদি আগে `USER app` করতে, তাহলে `app` user এর root-owned ফাইলে `chown` চালানোর permission থাকত না — build fail হত।

**না ব্যবহার করলে কী হয়:**
লাইন ১০ এ user তৈরি করা হয়েছে কিন্তু সুইচ না করলে সব root হিসেবেই চলে — পুরো নিরাপত্তা ব্যবস্থা অকেজো হয়ে যায়।

**দর্শন — "Defense in Depth" (স্তরে স্তরে সুরক্ষা):**
> নিরাপত্তা ব্যবস্থা শুধু তৈরি করলেই হয় না, সক্রিয়ও করতে হয়। User তৈরি করে সুইচ না করা মানে তালা লাগিয়ে দরজা খোলা রাখা।

---

### লাইন ২৫ — Entrypoint

```dockerfile
ENTRYPOINT [ "sh", "/app/Docker/entrypoint.sh" ]
```

**কী করে:**
Container শুরু হলে কোন কমান্ড চলবে তা নির্ধারণ করে। **Exec form** (JSON array) ব্যবহার করা হয়েছে।

**Exec form বনাম Shell form:**

| | Shell Form | Exec Form |
|---|---|---|
| Process | `/bin/sh -c` এর child | সরাসরি PID 1 |
| Signal handling | `SIGTERM` app এ পৌঁছায় না | `SIGTERM` সরাসরি app পায় |
| `docker stop` | App force-kill হতে পারে | App gracefully বন্ধ হয় |

**কেন external script?**
entrypoint.sh dev/prod ভেদে আলাদা কমান্ড চালায়। Dockerfile এ inline রাখলে পরিচালনা কঠিন হয়।

**দর্শন — "PID 1 ও Graceful Shutdown":**
> Container এ PID 1 প্রক্রিয়াই OS signal পায়। Exec form নিশ্চিত করে আপনার app PID 1 — যাতে `docker stop` করলে app সুন্দরভাবে বন্ধ হয়, হঠাৎ kill না হয়।

---
---

## Part 2 — entrypoint.sh

---

```sh
#!/bin/sh
```

**কী করে:**
Shebang লাইন — OS কে বলে এই script `/bin/sh` দিয়ে চালাতে।

**কেন `/bin/sh` এবং `/bin/bash` নয়?**
`/bin/sh` বেশি portable — Alpine Linux সহ সব image এ কাজ করে। এই script এ bash-specific কোনো feature নেই, তাই `/bin/sh` সঠিক পছন্দ।

---

```sh
if [ "$#" -gt 0 ]; then
  exec "$@"
fi
```

**কী করে:**
- `$#` = container কে দেওয়া argument এর সংখ্যা।
- `$@` = সব argument।
- কোনো argument থাকলে, `exec` দিয়ে সেই কমান্ড চালায় এবং shell কে replace করে।

**কেন `exec` ব্যবহার?**
`exec` shell কে replace করে — কমান্ড নিজেই PID 1 হয়। `exec` ছাড়া shell একটি child process তৈরি করত, signal handling ভেঙে যেত।

**ব্যবহারিক উদাহরণ:**
```bash
docker run myimage python manage.py migrate        # migration চালাবে
docker run myimage python manage.py createsuperuser # admin তৈরি করবে
docker run myimage sh                              # debug shell
docker run myimage                                 # web server চালাবে
```

**দর্শন — "One Image, Many Roles" (এক ইমেজ, অনেক কাজ):**
> একটি ইমেজ দিয়ে web server, migration runner, shell — সব করা যাবে। আলাদা image বানানোর দরকার নেই।

---

```sh
PORT=${PORT:-8011}
```

**কী করে:**
`$PORT` environment variable থাকলে সেটা ব্যবহার করে, না থাকলে default `8011` ব্যবহার করে।

**কেন ব্যবহার করা হয়:**
- Port ইমেজ rebuild ছাড়াই পরিবর্তন করা যায়।
- Heroku, Render, Railway — এরা runtime এ `$PORT` inject করে।
- dev, staging, prod — সবার port আলাদা হতে পারে।

**না ব্যবহার করলে কী হয়:**
Port hardcoded হয়ে যায় — পরিবর্তন করতে হলে নতুন image build করতে হবে।

**দর্শন — "12-Factor App: Config via Environment":**
> Port, secret, database URL — সব কিছু environment variable থেকে আসবে, code বা Dockerfile এ hardcode হবে না।

---

```sh
if [ "$(echo $DJANGO_DEV | tr '[:upper:]' '[:lower:]')" = "true" ]; then
  exec python manage.py runserver 0.0.0.0:$PORT
```

**কী করে:**
- `DJANGO_DEV` variable lowercase করে চেক করে (`TRUE`, `True`, `true` সব কাজ করে)।
- যদি `true` হয়, Django এর built-in development server চালায়।

**কেন dev server?**
- Code change এ auto-reload হয়।
- Detailed error page দেখায়।
- কোনো worker/thread management লাগে না।

**কেন production এ কখনো নয়?**
- Single-threaded — একসাথে একটিই request handle করতে পারে।
- Django নিজেই বলে: *"এই server production এ ব্যবহার করবেন না।"*

**দর্শন — "Environment Parity with Safety Guards":**
> Dev এবং prod একই image চালাবে, কিন্তু critical পার্থক্য (dev server বনাম gunicorn) environment variable দিয়ে নিয়ন্ত্রিত হবে — দুর্ঘটনাবশত production এ dev server চলা অসম্ভব।

---

```sh
else
  exec gunicorn medihub.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 4 \
    --threads 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
fi
```

**কী করে:**
Production-grade Python WSGI server **Gunicorn** চালায়।

| Flag | মান | অর্থ |
|---|---|---|
| `medihub.wsgi:application` | Django app | কোন WSGI callable serve করবে |
| `--bind 0.0.0.0:$PORT` | সব interface | সব network interface এ listen করে |
| `--workers 4` | ৪টি process | ৪টি আলাদা worker প্রক্রিয়া |
| `--threads 2` | প্রতি worker এ ২ thread | মোট ৮টি concurrent request handle করতে পারে |
| `--timeout 60` | ৬০ সেকেন্ড | ৬০ সেকেন্ডে response না দিলে worker kill করে |
| `--access-logfile -` | stdout | access log সরাসরি stdout এ |
| `--error-logfile -` | stderr | error log সরাসরি stderr এ |

**`0.0.0.0` কেন?**
`127.0.0.1` দিলে শুধু container এর ভেতর থেকে access হয়। `0.0.0.0` মানে সব network interface এ শোনো — বাইরে থেকে request আসতে পারবে।

**4 workers কেন?**
একটি common formula: `(2 × CPU core) + 1`। ২-core সার্ভারে ৫টি worker ভালো। ৪ একটি নিরাপদ default।

**`--timeout 60` কেন?**
কোনো request hang করলে (database slow, infinite loop), Gunicorn ৬০ সেকেন্ড পর সেই worker kill করে নতুন একটি শুরু করে — একটি bad request পুরো worker block করতে পারে না।

**`-` কেন log file হিসেবে?**
`-` মানে stdout/stderr। Container restart এ ভেতরের ফাইল হারিয়ে যায়। stdout এ পাঠালে Docker, Kubernetes, বা Datadog/CloudWatch সব log ধরে রাখতে পারে।

**`exec` কেন?**
Gunicorn কে PID 1 বানাতে — যাতে `SIGTERM` সরাসরি পায় এবং gracefully বন্ধ হতে পারে।

**দর্শন — "Cattle, not Pets" ও "Stateless Processes":**
> Container অস্থায়ী। Log বা file container এর ভেতরে রাখো না। Log বাইরে stream করো। Gunicorn workers দিয়ে horizontal scaling করো — বড় সার্ভার নয়, বেশি container চালাও।

---

## সারসংক্ষেপ — পুরো ছবি

```
python:3.11-slim          ← ছোট ও নিরাপদ base
ENV flags                 ← Python এর সঠিক runtime আচরণ
WORKDIR /app              ← পরিচিত project root
System deps install       ← শুধু যা দরকার
Non-root user তৈরি        ← নিরাপত্তার জন্য least privilege
requirements.txt আগে     ← Docker layer cache সর্বোচ্চ ব্যবহার
pip install               ← পুনরুৎপাদনযোগ্য dependency install
Source code কপি           ← সবার শেষে, cache bust এড়াতে
chmod + mkdir + chown     ← Build time এই runtime প্রস্তুতি
USER app                  ← নিরাপত্তা সক্রিয়
ENTRYPOINT                ← PID 1, graceful signal handling
```

```
entrypoint.sh
├── exec "$@"             ← যেকোনো management command চালানোর সুযোগ
├── PORT default          ← Runtime configurable port
├── DJANGO_DEV=true       ← Dev server (hot reload, debug)
└── else                  ← Gunicorn (production, concurrent)
```

### ব্যবহৃত মূল দর্শনসমূহ

| দর্শন | কোথায় প্রয়োগ হয়েছে |
|---|---|
| **Minimal Attack Surface** | `slim` image, non-root user, `--no-install-recommends` |
| **Layer Cache Optimization** | `requirements.txt` আগে, source code পরে |
| **12-Factor App** | Port ও mode এর জন্য env var, stdout এ log |
| **Least Privilege** | `adduser --system`, `USER app` |
| **Graceful Shutdown** | সর্বত্র `exec` form, Gunicorn `--timeout` |
| **Fail Fast** | Build time এ `mkdir` ও `chown` |
| **One Image, Many Roles** | entrypoint এ `exec "$@"` escape hatch |
