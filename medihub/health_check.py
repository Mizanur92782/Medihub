import socket
from django.shortcuts import render
from datetime import datetime

def HealthCheck(request):
  now = datetime.now()
  return render(request, 'health.html', {
    "host": request.get_host(),
    "container": socket.gethostname(),
    "fullpath": request.build_absolute_uri(),
    "server_time": now.strftime('%H:%M:%S'),
    "server_date": now.strftime('%A, %d %B %Y'),
    "last_updated": now.strftime('%d %b %Y — %H:%M:%S'),
  })
