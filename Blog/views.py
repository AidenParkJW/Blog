import calendar
from datetime import timedelta, date

from allauth.socialaccount.models import SocialAccount
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.sessions.models import Session
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.db.models.functions import Extract
from django.shortcuts import render
from django.urls import reverse_lazy, exceptions
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from Blog.forms import UserProfileForm
from menu.models import Menu
from post.models import Post


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        
        # 1. The latest 10 Posts
        qs01 = Post.objects.select_related("menu").all().order_by("-post_uid")
        if not self.request.user.is_superuser:
            qs01 = qs01.filter(menu__menu_isEnabled=True, post_isEnabled=True)
        qs01 = qs01[0:10]
        
        # 2. 10 by many views
        qs02 = Post.objects.select_related("menu").all().order_by("-post_views")
        if not self.request.user.is_superuser:
            qs02 = qs02.filter(menu__menu_isEnabled=True, post_isEnabled=True)
        qs02 = qs02[0:10]
        
        # 3. Monthly Registered Post for the Last 1 year
        _today = date.today()
        _d = date(_today.year - 1, _today.month + 1, 1)
        _lastDay = 0
        
        qs03 = Post.objects.select_related("menu").annotate(yyyy=Extract("post_crte_dt", "year"), mm=Extract("post_crte_dt", "month")).values("yyyy", "mm").annotate(post_cnt=Count("*")).filter(post_crte_dt__gt=_d).order_by("yyyy", "mm")
        if not self.request.user.is_superuser:
            qs03 = qs03.filter(menu__menu_isEnabled=True, post_isEnabled=True)
        
        _list01 = []
        for i in range(12):
            _d = _d + timedelta(days = _lastDay)
            _lastDay = calendar.monthrange(_d.year, _d.month)[1]
            
            _post_cnt = 0
            for _q in qs03:
                if _q["yyyy"] == _d.year and _q["mm"] == _d.month:
                    _post_cnt = _q["post_cnt"]
                    break
            
            _list01.append(dict({"yyyy": _d.year, "mm": "{:02}".format(_d.month), "post_cnt": _post_cnt}))
        
        # 4. Access Statistics for the Last 2 Month
        _d = _today - timedelta(days = 60)
        qs04 = Session.objects.annotate(mm=Extract("expire_date", "month"), dd=Extract("expire_date", "day")).values("mm", "dd").annotate(cnt=Count("*")).filter(expire_date__gt=_d).order_by("mm", "dd")
        
        _list02 = []
        for i in range(60):
            _d = _d + timedelta(days = 1)
            
            _cnt = 0
            for _q in qs04:
                if _q["mm"] == _d.month and _q["dd"] == _d.day:
                    _cnt = _q["cnt"]
                    break
        
            _mmdd = "{:02}/{:02}".format(_d.month, _d.day) if i == 0 or _d.day == 1 else "{:02}".format(_d.day)
            _list02.append(dict({"mmdd": _mmdd, "cnt": _cnt}))
        
        # 5. Percentage of Post Registration Category for the Last 6 Months
        _today = date.today()
        _d = _today - timedelta(days = 180)
        qs05 = Menu.objects.values("menu_name").annotate(post_cnt=Count("menu_post", filter=Q(menu_post__post_isEnabled=True, menu_post__post_crte_dt__gt=_d))).filter(menu_isEnabled=True).filter(post_cnt__gt=0).order_by("-post_cnt", "menu_name")[0:10]
        
        # 6. Percentage of Post Registration Category for total period
        qs06 = Menu.objects.values("menu_name").annotate(post_cnt=Count("menu_post", filter=Q(menu_post__post_isEnabled=True))).filter(menu_isEnabled=True).filter(post_cnt__gt=0).order_by("-post_cnt", "menu_name")[0:10]
        
        context["postsLatest"]      = qs01
        context["postsViews"]       = qs02
        context["postsYears"]       = _list01
        context["connStatics"]      = _list02
        context["menuStatics6M"]    = qs05
        context["menuStaticsALL"]   = qs06
        return context


class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("register_done")
    
class UserCreateDoneTV(TemplateView):
    template_name = "registration/register_done.html"


@method_decorator(login_required, name="dispatch")
class UserUpdateView(UpdateView):
    form_class = UserProfileForm
    template_name = "registration/profile.html"
    success_url = reverse_lazy("profile_done")
    
    def get_object(self, queryset=None):
        # user = User.objects.get(id=self.request.user.id)
        # Allow when it doesn't have a social account.
        # In other word, It logged in base our system's account that wasn't logged in via social login.
        try:
            user = User.objects.exclude(id__in=SocialAccount.objects.all().values("user_id")).get(id=self.request.user.id)
        except User.DoesNotExist:
            raise PermissionDenied
        
        return user
    
class UserUpdateDoneTV(TemplateView):
    template_name = "registration/profile_done.html"
    
    
@method_decorator(login_required, name="dispatch")
class UserDeleteView(DeleteView):
    mode = User
    template_name = "registration/withdraw.html"
    success_url = reverse_lazy("withdraw_done")

    def get_object(self, queryset=None):
        return User.objects.get(id=self.request.user.id)

class UserDeleteDoneTV(TemplateView):
    template_name = "registration/withdraw_done.html"


@method_decorator(login_required, name="dispatch")
class UserPasswordChangeView(PasswordChangeView):
    template_name = "registration/password_change.html"
    success_url = reverse_lazy("password_change_done")

class UserPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = "registration/password_change_done.html"


class UserPasswordResetView(PasswordResetView):
    template_name = "registration/password_reset.html"
    success_url = reverse_lazy("password_reset_done")

class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = "registration/password_reset_done.html"


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "registration/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")

class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "registration/password_reset_complete.html"


# custom error page
class HttpErrorView():
    @classmethod
    def error400(cls, request, exception=None):
        errorCode = 400
        errorMsg = "Bad Request"
        return render(request, "error/error.html", {"error_code":errorCode, "error_msg":errorMsg}, status=errorCode)

    @classmethod
    def error403(cls, request, exception=None):
        errorCode = 403
        errorMsg = "Forbidden (Permission Denied)"
        return render(request, "error/error.html", {"error_code":errorCode, "error_msg":errorMsg}, status=errorCode)

    @classmethod
    def error404(cls, request, exception=None):
        errorCode = 404
        if isinstance(exception, exceptions.Resolver404):
            errorMsg = "Page Not Found"
        else:
            errorMsg = exception
            
        return render(request, "error/error.html", {"error_code":errorCode, "error_msg":errorMsg}, status=errorCode)

    @classmethod
    def error500(cls, request, exception=None):
        errorCode = 500
        errorMsg = "Server Error"
        return render(request, "error/error.html", {"error_code":errorCode, "error_msg":errorMsg}, status=errorCode)
