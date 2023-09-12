from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("reg", views.reg, name="reg"),
    path("heartbeat", views.reg, name="heartbeat"),
    path("dereg", views.dereg, name="dereg"),
    path("admin_console",views.get_admin_console,name="admin_console")
]