import os, shutil, pathlib, mimetypes

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.db.models import Q
from django.dispatch.dispatcher import Signal
from django.http.response import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView, DeleteView

from attFile.models import AttFile
from menu.models import Menu
from page.forms import PageForm
from page.models import Page, updateIsEnabled
from django.db.models.signals import post_save



# Detail View
class PageDV(DetailView):
    model = Page
    template_name ="page/page_detail.html"
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        
        if self.object.page_uid is None:
            if not self.request.user.is_superuser:
                raise Http404("Page does not exist")
            
            return redirect(self.object.get_create_url())
        
        else:
            return self.render_to_response(context)
    
    # override
    def get_object(self, queryset=None):
        try:
            # It is different from having a 'select_related' syntax.
            # If there is no 'select_related' syntax, when refer to the menu object, the menu selection query runs one more time.
            page = Page.objects.select_related("menu").select_related("page_crte_user").get(Q(page_isEnabled=True) & Q(menu__menu_uid=self.kwargs["menu_uid"]))
            
            # check permission
            if not self.request.user.is_superuser:
                if not page.menu.menu_isEnabled or not page.page_isEnabled:
                    raise PermissionDenied
            
            '''
            https://docs.djangoproject.com/en/3.0/topics/signals/#django.dispatch.Signal.connect
            https://docs.djangoproject.com/en/3.0/topics/signals/#disconnecting-signals
            
            Signal disconnect is required to prevent post_save signal.
            Otherwise, unnecessary page_isEnabled update occurs.
            And after the work is done, signal connect is needed again.
            '''
            # UPDATE for page_views + 1
            if Signal.disconnect(post_save, receiver=updateIsEnabled, sender=Page):
                page.page_views += 1
                page.save(update_fields=["page_views"])
                Signal.connect(post_save, receiver=updateIsEnabled, sender=Page)
            
        except Page.DoesNotExist as e:
            page = Page()
            page.menu = Menu.objects.get(menu_uid=self.kwargs["menu_uid"])
            
        return page
    
    # override
    def get_context_data(self, **kwargs):
        context = DetailView.get_context_data(self, **kwargs)
        context["menu_paths"] = self.object.menu.getMenuPath()
        context["images"] = AttFile.objects.filter(Q(page__page_uid=self.object.page_uid) & Q(att_isImage=True))
        return context

# Edit(Create/Update) View
@method_decorator(login_required, name="dispatch")
class PageEV(UpdateView):
    form_class = PageForm
    template_name = "page/page_form.html"
    
    # override
    def get_object(self, queryset=None):
        # check permission
        if not self.request.user.is_superuser:
            raise PermissionDenied
        
        page_uid = self.kwargs.get("page_uid", None)
        
        # When coming via pageCV
        if page_uid is None:
            try:
                page = Page()
                # for paeg's menu and making history.back url
                page.menu = Menu.objects.get(menu_uid=self.kwargs["menu_uid"])

            except Menu.DoesNotExist as e:
                raise Http404("Menu does not exist")

            return page
        
        # When coming via pageUV
        else:
            try:
                page = Page.objects.select_related("menu").select_related("page_crte_user").get(page_uid=page_uid)
            
            except Page.DoesNotExist as e:
                raise Http404("Page does not exist")

            return page
    
    # for passing arguments from views to forms
    # override
    def get_form_kwargs(self):
        kwargs = UpdateView.get_form_kwargs(self)
        kwargs["initial"]["request"] = self.request
        return kwargs

    # override
    def get_context_data(self, **kwargs):
        context = UpdateView.get_context_data(self, **kwargs)
        context["isEditable"] = True
        context["menu_paths"] = self.object.menu.getMenuPath()
        context["historyBack"] = self.object.get_absolute_url()
        context["other_pages"] = Page.objects.filter(menu=self.object.menu)
        return context

    # override
    def form_invalid(self, form):
        # https://docs.djangoproject.com/en/3.0/ref/forms/api/#django.forms.Form.errors
        '''
        for field, errors in form.errors.items():
            for error in errors:
                print(form.fields[field].label + ": " + error)
        '''
        
        # change error field to label in error message
        errors_keys = tuple(form.errors.keys())
        for field in errors_keys:
            form.errors[form.fields[field].label] = form.errors[field]
            del form.errors[field]
        
        # Deleting temporary directory
        _tempDir = os.path.join(settings.UPLOAD_TEMP, self.request.META.get("CSRF_COOKIE"))
        shutil.rmtree(_tempDir, ignore_errors=True)
    
        return UpdateView.form_invalid(self, form)

    # override
    def form_valid(self, form):
        if self.object.page_uid is None:
            form.instance.page_crte_user = self.request.user
            form.instance.page_mdfy_user = self.request.user
        else:
            form.instance.page_mdfy_user = self.request.user
            
        self.object = form.save()
        
        # If there is an attachment.
        _tempDir = os.path.join(settings.UPLOAD_TEMP, self.request.META.get("CSRF_COOKIE"))
        if os.path.exists(_tempDir):
            for _file in pathlib.Path(_tempDir).iterdir():
                attFile = AttFile()
                attFile.att_name        = _file.name
                '''
                https://docs.python.org/3/library/mimetypes.html?highlight=mimetypes#mimetypes.guess_type
                The return value is a tuple (type, encoding)
                '''
                _mime = mimetypes.guess_type(_file.name)[0]
                attFile.att_isImage     = (_mime is not None and _mime.startswith("image/"))
                attFile.att_desc        = None
                attFile.content_object  = self.object
                attFile.att_crte_user   = self.request.user
                attFile.att_mdfy_user   = self.request.user

                # With closes properly also on exceptions
                with open(_file, "rb") as fh:
                    # Get the content of the file, we also need to close the content file
                    with ContentFile(fh.read()) as _fileContent:
                        attFile.att_file.save(_file.name, _fileContent)
            
            # delete temporary directory
            shutil.rmtree(_tempDir, ignore_errors=True)
        
        ''' 
        Call order
        0. view.is_valid()
        1. view.form_valid or view.form_invalid
        2. form.save
        3. model.save
        
        success_url : UpdateView -> BaseUpdateView -> ModelFormMixin -> FormMixin.form_valid
        '''
        #return UpdateView.form_valid(self, form)
        return redirect(self.object.get_absolute_url())


# Delete View
@method_decorator(login_required, name="dispatch")
class PageRV(DeleteView):
    model = Page
    template_name = "page/page_delete.html"
    success_url = None
    
    # override
    def get_object(self, queryset=None):
        # check permission
        if not self.request.user.is_superuser:
            raise PermissionDenied
        
        try:
            page = Page.objects.select_related("menu").select_related("page_crte_user").get(page_uid=self.kwargs["page_uid"])
        
        except Page.DoesNotExist as e:
            raise Http404("Page does not exist")
        
        self.success_url = page.get_absolute_url()
        
        return page

    # override
    def get_context_data(self, **kwargs):
        context = DeleteView.get_context_data(self, **kwargs)
        context["menu_paths"] = self.object.menu.getMenuPath()
        return context


