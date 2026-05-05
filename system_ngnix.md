Context
ওহ বুঝেছি! তুমি বলছো:

Browser
↓
System Nginx (তোমার PC তে installed)
↓
Docker Nginx (container এ)
↓
Django (web container)

Copy
এই setup এ দুইটা Nginx আছে — একটা host machine এ, একটা Docker এ।

Static/Media Files এর সমস্যা
এই setup এ Docker nginx এর volume /var/lib/docker/volumes/ এ আছে — কিন্তু System Nginx সেখানে access করতে পারবে না।

Solution — System Nginx কে Bypass করো
System Nginx শুধু reverse proxy হিসেবে কাজ করবে, static files serve করবে না:

# System Nginx config (/etc/nginx/sites-available/medihub)

server {
listen 80;
server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:8080;  # Docker nginx এ পাঠাও
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

}

Copy
nginx
সব কাজ Docker Nginx করবে:

System Nginx → সব request Docker Nginx এ পাঠাবে
Docker Nginx → static/media volume থেকে serve করবে
Docker Nginx → বাকি request Django তে পাঠাবে

Copy
Flow
Browser → System Nginx (port 80)
↓ proxy_pass localhost:8080
Docker Nginx (port 8080)
↓ ↓
/static/ /media/ / (বাকি সব)
volume থেকে serve Django container

Copy
এভাবে static/media files এর জন্য আলাদা কিছু করতে হবে না — Docker Nginx নিজেই handle করবে। ✅
