# 🔧 Feed Engine — সম্পূর্ণ ব্যাখ্যা

---

## Feed Engine আসলে কী?

**Feed Engine** হলো একটা **scoring system**। এটা প্রতিটা Doctor-কে একটা score দেয়, তারপর সেই score অনুযায়ী sort করে user-কে দেখায়।

> 💡 **মূল প্রশ্ন:** _"কোন Doctor টা এই User-এর জন্য সবচেয়ে relevant?"_ — এই প্রশ্নের উত্তর বের করাই Feed Engine-এর কাজ।

যে Doctor-এর score যত বেশি, সে feed-এ তত উপরে থাকবে।

---

## পুরো Flow একনজরে

```
User Request আসলো
       ↓
Cache চেক করো  ──── HIT ──→  সরাসরি return করো (engine চলে না)
       ↓ MISS
Filter apply করো (division / district / specialization)
       ↓
DoctorFeedEngine চালাও
       ↓
প্রতিটা Doctor-এর Score calculate করো
       ↓
Score অনুযায়ী Sort করো
       ↓
Exploration apply করো (একটু randomness দাও)
       ↓
Paginate করো (20টা করে)
       ↓
Serialize করো (JSON বানাও)
       ↓
Cache-এ save করো (১ দিনের জন্য)
       ↓
User-কে response দাও
```

---

## Score কীভাবে Calculate হয়?

একটা Doctor-এর total score হলো **৭টা আলাদা score-এর যোগফল**, একটা penalty বাদ দিয়ে।

```
Total Score =
    base_score
  + personalization_score
  + location_score
  + quality_score
  + activity_score
  + trending_score
  + new_doctor_boost
  - repetition_penalty
```

---

### ১. Base Score — Doctor কতটা Popular?

| Signal | Weight | Multiplier |
|---|---|---|
| `total_profile_views` | × 1 | × 0.1 |
| `total_followers` | × 5 | × 0.6 |
| `total_questions` | × 4 | × 0.5 |
| `total_booking` | × 15 | — |

```python
base_score = (
    stats.total_profile_views * 1  * 0.1 +
    stats.total_followers     * 5  * 0.6 +
    stats.total_questions     * 4  * 0.5 +
    stats.total_booking       * 15
)
```

> **Logic:** Booking সবচেয়ে বেশি weight পায় (15), কারণ কেউ booking করলে সেটা সবচেয়ে strong signal যে Doctor টা ভালো। Profile view সবচেয়ে কম weight পায়, কারণ শুধু দেখলেই কিছু প্রমাণ হয় না।

---

### ২. Personalization Score — User-এর Interest কী?

```python
# User আগে কোন specialization-এর Doctor দেখেছে বা interact করেছে
# সেটা UserDoctorInterest table-এ score হিসেবে জমা থাকে

personalization_score = interest_score * 20 * 0.25
```

> **Logic:** ধরো একজন User বারবার Cardiologist দেখছে। তার মানে তার heart-এর সমস্যা আছে। তাই পরের বার feed-এ Cardiologist-দের আগে দেখাবে। এটাই **Personalization** — Netflix যেভাবে তোমার দেখা movie অনুযায়ী recommend করে, ঠিক সেভাবে।

---

### ৩. Location Score — Doctor কতটা কাছে?

| অবস্থান | Points |
|---|---|
| Same District | +25 |
| Same Division | +10 |
| অন্য জায়গা | 0 |

> **Logic:** রোগী সবসময় কাছের Doctor চায়। ঢাকার রোগীকে চট্টগ্রামের Doctor দেখানো কোনো কাজের না। তাই same district-এ হলে সবচেয়ে বেশি boost।

---

### ৪. Quality Score — Doctor কতটা ভালো?

```python
quality_score = (
    avg_rating * 10   # rating যত বেশি, score তত বেশি
    + 15 if is_verified         # verified Doctor-কে extra boost
    + 10 if profile_completed   # পুরো profile fill করলে boost
)
```

> **Logic:** ৫ star rating-এর Doctor পাবে `5 × 10 = 50` points। Verified badge মানে platform trust করে এই Doctor-কে, তাই extra 15। এটা **Quality Signal**।

---

### ৫. Activity Score — Doctor কতটা Active?

```python
activity_score = (
    10 if is_online              # এখন online আছে
    + 5 if last_active <= 1 day  # গতকালও active ছিল
)
```

> **Logic:** Online Doctor মানে সে এখনই reply দিতে পারবে। Inactive Doctor-কে feed-এ উপরে দেখানো মানে User হতাশ হবে। তাই active থাকলে boost।

---

### ৬. Trending Score — Doctor কি এখন Popular হচ্ছে?

```python
trending_score = total_feed_click * 0.5
```

> **Logic:** অনেকে feed-এ দেখে click করছে মানে Doctor টা এখন trending। এটা **Social Proof** — অনেকে দেখছে মানে ভালো কিছু আছে।

---

### ৭. New Doctor Boost — নতুন Doctor-কে সুযোগ দাও

```python
new_doctor_boost = 8 if created <= 30 days ago else 0
```

> **Logic:** নতুন Doctor-এর কোনো follower নেই, booking নেই, তাই base score কম। কিন্তু সে ভালো Doctor হতে পারে। তাই প্রথম ৩০ দিন extra boost দাও যাতে সে দেখা পায়। এটা **Cold Start Problem**-এর solution।

---

### ৮. Repetition Penalty — একই Doctor বারবার দেখাবো না

```python
repetition_penalty = impression_count * 10 * 0.2
```

> **Logic:** User যদি একটা Doctor-কে ৫ বার দেখে কিন্তু click না করে, মানে সে interested না। তাই যত বেশি দেখানো হয়েছে, তত বেশি penalty। এটা **Diversity** নিশ্চিত করে।

---

## N+1 Problem — এটা কী এবং কীভাবে Solve করলাম?

### ❌ আগের ভুল (N+1 Query Problem)

```python
# 1000 Doctor থাকলে 1000 বার DB query হতো
for doctor in doctors:                           # 1 query
    interest = UserDoctorInterest.objects \
                .filter(user=self.user, ...).first()   # +1 query প্রতি doctor

    count = DoctorFeedImpression.objects \
                .filter(user=self.user, ...).count()   # +1 query প্রতি doctor

# মোট = 1 + 1000 + 1000 = 2001 queries! 💀
```

### ✅ এখনকার সঠিক Solution

```python
# Loop-এর আগেই সব data এক বারে নিয়ে নাও
interests = {
    i.specialization_id: i.score
    for i in UserDoctorInterest.objects.filter(user=self.user)
}  # মাত্র 1 query

impression_counts = {
    i["doctor_id"]: i["total"]
    for i in DoctorFeedImpression.objects
    .filter(user=self.user).values("doctor_id").annotate(total=Count("id"))
}  # মাত্র 1 query

# এখন loop-এ শুধু dictionary lookup — কোনো DB query নেই
for doctor in doctors:
    score = interests.get(doctor.specialization_id, 0)  # O(1)
```

**মোট queries = মাত্র ৩টা** (doctors + interests + impressions), যাই হোক না কেন কতজন Doctor আছে।

---

## Exploration — কেন পুরো Shuffle করা ভুল ছিল?

### ❌ আগের ভুল

```python
random.shuffle(top)  # top 30 কে পুরো random করে দাও
```

এতে score 95-এর Doctor আর score 10-এর Doctor একই সুযোগ পায়। Ranking-এর কোনো মানে থাকে না।

### ✅ সঠিক পদ্ধতি — Epsilon-Greedy

```python
item["score"] += random.uniform(0, 2)  # সামান্য noise যোগ করো
top.sort(...)                          # তারপর আবার sort করো
```

এতে score 95-এর Doctor প্রায় সবসময়ই উপরে থাকবে, কিন্তু মাঝে মাঝে score 93 বা 94-এর Doctor উপরে আসতে পারে।

> এটা **Exploration vs Exploitation** — নতুন Doctor-দের একটু সুযোগ দাও, কিন্তু best Doctor-কে সরিয়ে দিও না।

---

## Cache Logic — কেন এবং কীভাবে?

```
User Request
     ↓
Cache-এ আছে? ──YES──→ সরাসরি return (0 DB query, super fast ⚡)
     ↓ NO
Engine চালাও (DB queries হলো)
     ↓
Result টা Cache-এ রাখো ১ দিনের জন্য
     ↓
Return করো
```

### Cache Key Design

```
feed:v1:42:div_1:dis_3:spec_5
         ↑     ↑      ↑      ↑
      user_id  div  district  spec
```

- User 42 যদি `district=3, specialization=5` দিয়ে filter করে → আলাদা cache entry
- User 42 যদি কোনো filter ছাড়া দেখে → আলাদা cache entry

### Random TTL Jitter কেন?

১০,০০০ user-এর cache যদি একসাথে expire করে, তাহলে একসাথে ১০,০০০ DB query আসবে — **server crash**।

তাই প্রতিটার TTL-এ `0–60 seconds` random যোগ করা হয়। এটাকে বলে **Cache Avalanche Prevention**।

---

## পুরো Architecture এক লাইনে

```
Filter করো → Score দাও → Sort করো → একটু Randomness দাও → Cache করো → দেখাও
```

> এটাই industry-তে যেকোনো বড় platform (LinkedIn, Practo, Zocdoc)-এর feed-এর মূল কাঠামো।
