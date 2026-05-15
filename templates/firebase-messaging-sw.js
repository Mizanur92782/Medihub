importScripts("https://www.gstatic.com/firebasejs/10.12.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/10.12.0/firebase-messaging-compat.js");

firebase.initializeApp({
  apiKey:            "AIzaSyAG5hH0fVRp9cC8nFT6rpQfNgnhgk5Bt5Q",
  authDomain:        "medihub-71ab9.firebaseapp.com",
  projectId:         "medihub-71ab9",
  storageBucket:     "medihub-71ab9.firebasestorage.app",
  messagingSenderId: "531622546348",
  appId:             "1:531622546348:web:1d4e61974244c14b7c8809"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  self.registration.showNotification(payload.notification.title, {
    body: payload.notification.body,
  });
});
