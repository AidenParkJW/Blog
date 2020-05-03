from django.core.exceptions import PermissionDenied
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy, exceptions
from Blog.forms import UserProfileForm
from allauth.socialaccount.models import SocialAccount
import inspect

class HomeView(TemplateView):
    template_name = "home.html"


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
