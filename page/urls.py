from django.urls import path
from page.views import *

app_name = "page"
urlpatterns = [
    path("<int:menu_uid>/"          , PageDV.as_view(), name="pageDV"),
    path("<int:menu_uid>/create/"   , PageEV.as_view(), name="pageCV"),
    path("<int:page_uid>/update/"   , PageEV.as_view(), name="pageUV"),
    path("<int:page_uid>/delete/"   , PageRV.as_view(), name="pageRV"),
]