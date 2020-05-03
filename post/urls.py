#from django.conf.urls import url
from django.urls import path
from post.views import *

app_name = "post"
urlpatterns = [
    # /post/2/
    #re_path(r"^(?P<menu_uid>\d+)/$", PostLV.as_view(), name="postLV"),
    path("<int:menu_uid>/", PostLV.as_view(), name="postLV"),
    
    # /post/2/1/
    #re_path(r"^(?P<menu_uid>\d+)/(?P<post_uid>\d+)/$", PostDV.as_view(), name="postDV"),
    path("<int:menu_uid>/<int:post_uid>/", PostDV.as_view(), name="postDV"),
    
    # /post/2-1 for dusqus
    path("<int:menu_uid>-<int:post_uid>/", PostDV.as_view(), name="postDVforDisqus"),
    
    # /post/2/create
    path("<int:menu_uid>/create/", PostEV.as_view(), name="postCV"),
    
    # /post/65/update
    path("<int:post_uid>/update/", PostEV.as_view(), name="postUV"),
    
    # /post/65/delete
    path("<int:post_uid>/delete/", PostRV.as_view(), name="postRV"),
    
    # /post/search/
    path("search/", SearchLV.as_view(), name="search"),
    
    path("tag/<str:tag>/", PostTLV.as_view(), name="postTLV"),
    
    path("tag/", TagTV.as_view(), name="tagCloud"),

]
