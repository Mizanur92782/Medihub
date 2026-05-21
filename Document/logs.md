web1 ──┐
web2 ──┼──→ Promtail (log collector-agent) → Loki (log store-log db) → Grafana (dashboard-visualizer)
web3 ──┘







Promtail কীভাবে log collect করে সেটা পুরো process আকারে বুঝতে হলে মনে রাখতে হবে—এটা আসলে একটা **log agent**, যেটা continuously চলতে থাকে এবং বিভিন্ন source থেকে log নিয়ে Loki-তে পাঠায়। তোমার Docker setup অনুযায়ী Promtail মূলত দুইভাবে log collect করতে পারে: file-based logs (যেমন `/app/logs/web1`) এবং Docker container logs (via `docker.sock`)।

প্রথমে Promtail শুরু হলে সে তার `promtail.yml` configuration ফাইল পড়ে। এই ফাইলে বলা থাকে কোন জায়গা থেকে logs নিতে হবে, যেমন কোন folder বা কোন container। এরপর Promtail সেই path গুলো “watch” করতে শুরু করে। উদাহরণস্বরূপ, যদি `/app/logs/web1/*.log` লেখা থাকে, তাহলে Promtail ওই folder continuously monitor করে। মানে নতুন কোনো log line file-এ লেখা হলেই Promtail সেটা detect করতে পারে।

এরপর Promtail সেই log file গুলো open করে line-by-line পড়ে। এটা একবার পড়ে থেমে যায় না—বরং real-time ভাবে নতুন log line আসলে সেটাও capture করে। এই পর্যায়ে Promtail প্রতিটা log এর সাথে কিছু extra তথ্য বা **labels** যোগ করে, যেমন কোন app থেকে এসেছে (web1/web2/web3), কোন job-এর log, বা কোন container থেকে এসেছে। এই labels পরবর্তীতে Grafana-তে filter করার জন্য খুব গুরুত্বপূর্ণ।

তারপর Promtail সেই collected logs কে HTTP request এর মাধ্যমে Loki server-এ পাঠায়। এই process টা continuous চলে—মানে Promtail সবসময় background এ running থাকে এবং নতুন logs আসলেই সাথে সাথে Loki-তে push করে দেয়। Loki তখন এগুলো store করে রাখে এবং পরে query করার জন্য প্রস্তুত রাখে।

সোজা ভাষায় বললে, Promtail হলো একটা “watcher + reader + sender” system—এটা log file বা container watch করে, নতুন log line পড়ে, label যোগ করে, তারপর Loki-তে পাঠিয়ে দেয়। এজন্যই Promtail ছাড়া Loki কিছুই দেখতে পায় না, কারণ Loki নিজে logs collect করে না, শুধু receive আর store করে।

👉 এক লাইনে: Promtail continuously log sources watch করে, new log line detect করে, metadata যোগ করে, তারপর Loki-তে push করে দেয়।
