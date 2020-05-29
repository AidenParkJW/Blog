"""Blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('post/', include('post.urls'))
"""
from django.contrib import admin
from django.contrib.staticfiles.views import serve
from django.urls import path, include
from django.urls.conf import re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from Blog.views import HomeView, HttpErrorView \
    , UserCreateView, UserCreateDoneTV, UserUpdateView, UserUpdateDoneTV, UserDeleteView, UserDeleteDoneTV \
    , UserPasswordChangeView, UserPasswordChangeDoneView, UserPasswordResetView, UserPasswordResetDoneView, UserPasswordResetConfirmView, UserPasswordResetCompleteView

urlpatterns = [
    # Admin Mode
    path("~!Admin/", admin.site.urls),
    
    # The First Page
    path("", HomeView.as_view(), name="home"),
    
    # Authentication Pages
    path("accounts/"                                , include("django.contrib.auth.urls")),
    path("accounts/register/"                       , UserCreateView.as_view()                  , name="register"),
    path("accounts/register/done/"                  , UserCreateDoneTV.as_view()                , name="register_done"),
    path("accounts/profile/"                        , UserUpdateView.as_view()                  , name="profile"),
    path("accounts/profile/done/"                   , UserUpdateDoneTV.as_view()                , name="profile_done"),
    path("accounts/withdraw/"                       , UserDeleteView.as_view()                  , name="withdraw"),
    path("accounts/withdraw/done/"                  , UserDeleteDoneTV.as_view()                , name="withdraw_done"),
    path("accounts/password/change/"                , UserPasswordChangeView.as_view()          , name="password_change"),
    path("accounts/password/change/done/"           , UserPasswordChangeDoneView.as_view()      , name="password_change_done"),
    path("accounts/password/reset/"                 , UserPasswordResetView.as_view()           , name="password_reset"),
    path("accounts/password/reset/done/"            , UserPasswordResetDoneView.as_view()       , name="password_reset_done"),
    path("accounts/password/reset/<uidb64>/<token>/", UserPasswordResetConfirmView.as_view()    , name="password_reset_confirm"),
    path("accounts/password/reset/complete/"        , UserPasswordResetCompleteView.as_view()   , name="password_reset_complete"),

    # Social Login
    path("accounts/socialLogin/"                    , include("allauth.urls")),
    path("accounts/callback/"                       , TemplateView.as_view(template_name="registration/callback.html"), name="callback"),

    # The App Pages
    path("menu/"    , include("menu.urls")),
    path("post/"    , include("post.urls")),
    path("page/"    , include("page.urls")),
    path("attFile/" , include("attFile.urls")),
    
    # session info.
    path("session/" , TemplateView.as_view(template_name="session.html"), name="session"),
    
    # for Static file
    re_path(r"^static/(?P<path>.*)", serve, kwargs={"insecure":True})
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

handler400 = HttpErrorView.error400
handler403 = HttpErrorView.error403
handler404 = HttpErrorView.error404
handler500 = HttpErrorView.error500


# debug toolbar
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]






