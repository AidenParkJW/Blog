from django.urls import path
from attFile.views import AttFileAV

app_name = "attFile"
urlpatterns = [
    path("load/"                , AttFileAV.load        , name="load"),
    path("upload/"              , AttFileAV.upload      , name="upload"),
    path("download/<str:uid>/"  , AttFileAV.download    , name="download"),
    path("imageView/<str:uid>/" , AttFileAV.imageView   , name="imageView"),
    path("imageThumb/<str:uid>/", AttFileAV.imageThumb  , name="imageThumb"),
]