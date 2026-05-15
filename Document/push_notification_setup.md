# Push Notification Setup — Medihub

## How It Works
```
User opens app → Frontend gets FCM token → sends to Django API
→ Django saves token to Device model
→ When event happens → Django sends push via Firebase → User gets notification
```

---

## Backend Setup (Already Done ✅)

### 1. Firebase Credentials
- File: `medihub-71ab9-4495c5b58eb1.json` (in project root)
- Set in `.env`:
```
FIREBASE_CREDENTIALS_PATH=medihub-71ab9-4495c5b58eb1.json
```

### 2. Key Files
| File | Purpose |
|------|---------|
| `notification/models/psuh_not_model.py` | Stores device FCM tokens per user |
| `notification/servcies.py` | Sends push to one token or all user devices |
| `notification/views/push_notf_view.py` | API to register device + test push |
| `notification/urls.py` | Routes |

### 3. API Endpoints
| Method | URL | Purpose |
|--------|-----|---------|
| POST | `/notification/device/register/` | Save FCM token (requires JWT) |
| POST | `/notification/push/test/` | Send test push (requires JWT) |

### 4. Trigger Push From Any App
```python
from notification.servcies import PushNotification

# send to all devices of a user
PushNotification.send_to_user(user, "Title", "Message body")
```

---

## Frontend Setup

### Keys to Use
| Key | Value | Where |
|-----|-------|-------|
| Firebase Config | see below | initialize Firebase SDK |
| VAPID Key | `BIuuIgqcBPM5mPHAxGpQ3Ud7WptO551kuuA5yNiYIk7SbpW7nTqtzpX3X7JqMoqZVbjXxFe2C4V9W0p2QNPJchY` | `getToken()` — web only |

### Firebase Config
```js
const firebaseConfig = {
  apiKey:            "AIzaSyAG5hH0fVRp9cC8nFT6rpQfNgnhgk5Bt5Q",
  authDomain:        "medihub-71ab9.firebaseapp.com",
  projectId:         "medihub-71ab9",
  messagingSenderId: "531622546348",
  appId:             "1:531622546348:web:1d4e61974244c14b7c8809"
};
```

### Frontend Flow (3 Steps)
```
Step 1 — Initialize Firebase with config above

Step 2 — Get FCM token after user logs in
const token = await getToken(messaging, { vapidKey: "VAPID_KEY_HERE" });

Step 3 — Send token to backend
POST /notification/device/register/
Headers: { Authorization: "Bearer <jwt>" }
Body:    { "token": "<fcm_token>" }
```

### Android / iOS
- No VAPID key needed
- Just use `FirebaseMessaging.getInstance().getToken()` 
- Then POST to `/notification/device/register/`

---

## Summary
```
firebase-key.json  → backend only (never share with frontend)
VAPID key          → frontend web only
Firebase config    → frontend (web + mobile)
JWT token          → required when calling register API
```
