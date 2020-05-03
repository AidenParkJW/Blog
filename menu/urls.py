from django.urls import path
from menu.views import MenuAV

app_name = "menu"
urlpatterns = [
    path("load/", MenuAV.load, name="load")
]