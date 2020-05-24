from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, F
from django.http.response import Http404
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView, DeleteView
from tagging.views import TaggedObjectList

from attFile.models import AttFile
from attFile.views import AttFileNV
from menu.models import Menu
from post.forms import PostForm
from post.forms import PostSearchForm
from post.models import Post


# List View
class PostLV(ListView):
    model = Post
    template_name = "post/post_list.html"
    context_object_name = "posts"   #object_list
    paginate_by = 20
    __menu = None
    __srchWord = None

    # override (don't need here)
    def get(self, request, *args, **kwargs):
        return ListView.get(self, request, *args, **kwargs)

    # override for search
    def post(self, request, *args, **kwargs):
        self.__srchWord = self.request.POST["search_word"]
        return ListView.get(self, request, *args, **kwargs)

    # override
    def get_queryset(self):
        #print(inspect.stack()[0][3])
        
        try:
            self.__menu = Menu.objects.get(menu_uid=self.kwargs["menu_uid"])
            
            # check permission
            if not self.request.user.is_superuser:
                if not self.__menu.menu_isEnabled:
                    raise PermissionDenied
            
            #qs = Post.objects.select_related("menu").filter(menu__menu_uid=self.__menu.menu_uid)    # same below script
            qs = Post.objects.select_related("menu").filter(menu=self.__menu)
            
            if self.__srchWord:
                qs = qs.filter(Q(post_title__icontains=self.__srchWord) | Q(post_content__icontains=self.__srchWord))
            
            # If is not superuser.
            if not self.request.user.is_superuser:
                qs = qs.filter(post_isEnabled=True)
            
        except Menu.DoesNotExist as e:
            #raise Http404(e)
            raise Http404("Menu does not exist")
            
        return qs
    
    # override
    def get_context_data(self, *, object_list=None, **kwargs):
        #print(inspect.stack()[0][3])
        context = ListView.get_context_data(self, **kwargs)
        context["menu_path"] = self.__menu.getMenuPath()
        context["menu_uid"] = self.__menu.menu_uid
        context["search_word"] = self.__srchWord if self.__srchWord else ""
        return context


# Detail View
class PostDV(DetailView):
    model = Post
    template_name = "post/post_detail.html"
    
    # override
    def get_object(self, queryset=None):
        #print(inspect.stack()[0][3])
        try:
            # It is different from having a 'select_related' syntax.
            # If there is no 'select_related' syntax, when refer to the menu object, the menu selection query runs one more time.
            post = Post.objects.select_related("menu").select_related("post_crte_user").get(post_uid=self.kwargs["post_uid"])
            
            # check permission
            if not self.request.user.is_superuser:
                if not post.menu.menu_isEnabled or not post.post_isEnabled:
                    raise PermissionDenied
            
            # UPDATE for post_views + 1
            post.post_views += 1
            post.save(update_fields=["post_views"])
            
        except Post.DoesNotExist as e:
            raise Http404("Post does not exist")
        
        return post

    # override
    def get_context_data(self, **kwargs):
        #print(inspect.stack()[0][3])
        qs = Post.objects.select_related("menu").filter(menu=self.object.menu)
        
        # If is not superuser.
        if not self.request.user.is_superuser:
            qs = qs.filter(post_isEnabled=True)
        
        '''
        # blow script result is not post list, simple dict type
        qsUpper = qs.filter(post_uid__gte=self.object.post_uid).values("post_uid", "post_title", "post_crte_dt", menu_uid=F("menu__menu_uid")).order_by("post_uid")[0:6]
        qsLower = qs.filter(post_uid__lt=self.object.post_uid).values("post_uid", "post_title", "post_crte_dt", menu_uid=F("menu__menu_uid")).order_by("-post_uid")[0:5]
        
        listUpper = sorted(qsUpper, key=lambda item:item["post_uid"], reverse=True)
        listLower = sorted(qsLower, key=lambda item:item["post_uid"], reverse=True)
        '''
        
        qsUpper = qs.filter(post_uid__gte=self.object.post_uid).order_by("post_uid")[0:6]
        qsLower = qs.filter(post_uid__lt=self.object.post_uid).order_by("-post_uid")[0:5]
        
        listUpper = sorted(qsUpper, key=lambda post:post.post_uid, reverse=True)
        listLower = sorted(qsLower, key=lambda post:post.post_uid, reverse=True)
        
        _otherPosts = listUpper + listLower
        
        context = DetailView.get_context_data(self, **kwargs)
        context["isEditable"] = False
        context["menu_path"] = self.object.menu.getMenuPath()
        context["images"] = AttFile.objects.filter(Q(post__post_uid=self.object.post_uid) & Q(att_isImage=True))    # SQL equivalent: AttFile.objects.filter(post__post_uid=self.object.post_uid, att_isImage=True)
        context["other_posts"] = _otherPosts
        return context


# Edit(Create/Update) View
@method_decorator(login_required, name="dispatch")
class PostEV(UpdateView):
    form_class = PostForm
    template_name = "post/post_form.html"
    attFileNV = AttFileNV()
    
    # override
    def get_object(self, queryset=None):
        post_uid = self.kwargs.get("post_uid", None)
        
        # When coming via postCV
        if post_uid is None:
            try:
                post = Post()
                # for post's menu and making history.back url
                post.menu = Menu.objects.get(menu_uid=self.kwargs["menu_uid"])
                
                # check permission
                if not self.request.user.is_superuser:
                    if not post.menu.menu_isEnabled:
                        raise PermissionDenied
            
            except Menu.DoesNotExist as e:
                raise Http404("Menu does not exist")
        
            return post
        
        # When coming via postUV
        else:
            try:
                post = Post.objects.select_related("menu").select_related("post_crte_user").get(post_uid=post_uid)
                
                # check permission
                if not self.request.user.is_superuser:
                    if not post.menu.menu_isEnabled or not post.post_isEnabled:
                        raise PermissionDenied
                
                    if self.request.user.id != post.post_crte_user.id:
                        raise PermissionDenied
                
            except Post.DoesNotExist as e:
                raise Http404("Post does not exist")
            
            return post
    
    # For passing arguments from views to forms
    # override
    def get_form_kwargs(self):
        kwargs = UpdateView.get_form_kwargs(self)
        kwargs["initial"]["request"] = self.request
        return kwargs
    
    # override
    def get_context_data(self, **kwargs):
        context = UpdateView.get_context_data(self, **kwargs)
        context["isEditable"] = True
        context["menu_path"] = self.object.menu.getMenuPath()
        context["historyBack"] = self.object.get_list_url() if self.object.post_uid is None else self.object.get_absolute_url()
        return context
    
    # override
    def form_invalid(self, form):
        # https://docs.djangoproject.com/en/3.0/ref/forms/api/#django.forms.Form.errors
        '''
        for field, errors in form.errors.items():
            for error in errors:
                print(form.fields[field].label + ": " + error)
        '''
        
        # change error field to label in error messages
        errors_keys = tuple(form.errors.keys())
        for field in errors_keys:
            form.errors[form.fields[field].label] = form.errors[field]
            del form.errors[field]
        
        # Delete temporary directory
        self.attFileNV.rmTemp(self)
    
        return UpdateView.form_invalid(self, form)
    
    # override
    def form_valid(self, form):
        if self.object.post_uid is None:
            form.instance.post_crte_user = self.request.user
            form.instance.post_mdfy_user = self.request.user
        else:
            form.instance.post_mdfy_user = self.request.user
        
        self.object = form.save()
        
        # Save the actual AttFile object  and move uploaded file to object's directory
        self.attFileNV.save(self)
        
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
class PostRV(DeleteView):
    model = Post
    template_name = "post/post_delete.html"
    success_url = None

    # override
    def get_object(self, queryset=None):
        try:
            post = Post.objects.select_related("menu").select_related("post_crte_user").get(post_uid=self.kwargs["post_uid"])
            
            # check permission
            if not self.request.user.is_superuser:
                if not post.menu.menu_isEnabled or not post.post_isEnabled:
                    raise PermissionDenied
            
                if self.request.user.id != post.post_crte_user.id:
                    raise PermissionDenied
            
        except Post.DoesNotExist as e:
            raise Http404("Post does not exist")
        
        self.success_url = post.get_list_url()
        
        return post

    # override
    def get_context_data(self, **kwargs):
        context = DeleteView.get_context_data(self, **kwargs)
        context["menu_path"] = self.object.menu.getMenuPath()
        return context


# Search View
class SearchLV(ListView):
    model = Post
    template_name = "post/post_search.html"
    context_object_name = "posts"   #object_list
    paginate_by = 20
    __srchWord = None
    __count = 0
    # override
    def post(self, request, *args, **kwargs):
        self.__srchWord = self.request.POST["search_word"]
        return ListView.get(self, request, *args, **kwargs)

    # override
    def get_queryset(self):
        
        if self.__srchWord:
            qs = Post.objects.select_related("menu").filter(Q(post_title__icontains=self.__srchWord) | Q(post_content__icontains=self.__srchWord))
        
            # If is not superuser.
            if not self.request.user.is_superuser:
                qs = qs.filter(menu__menu_isEnabled=True).filter(post_isEnabled=True)
        
        else:
            qs = Post.objects.none()
            
        self.__count = len(qs)
        
        return qs

    # override
    def get_context_data(self, *, object_list=None, **kwargs):
        context = ListView.get_context_data(self, **kwargs)
        context["count"] = self.__count
        context["search_word"] = self.__srchWord if self.__srchWord else ""
        context["form"] = PostSearchForm(initial={"search_word": context["search_word"]})
        return context


# Post List of associated tag
class PostTLV(TaggedObjectList):
    model = Post
    template_name = "post/post_list_via_tag.html"
    context_object_name = "posts"   #object_list
    paginate_by = 20
    
    # override 
#     def get_queryset_or_model(self):
#         try:
#             qs = TaggedObjectList.get_queryset_or_model(self)
#             qs = qs.objects.select_related("menu")
#       
#             # If is not superuser.
#             if not self.request.user.is_superuser:
#                 qs = qs.filter(menu__menu_isEnabled=True).filter(post_isEnabled=True)
#                   
#         except Post.DoesNotExist as e:
#             qs = Post.objects.none()
#               
#         return qs
    
    # override 
    def get_queryset(self):
        try:
            qs = TaggedObjectList.get_queryset(self)
            qs = qs.select_related("menu")
        
            # If is not superuser.
            if not self.request.user.is_superuser:
                qs = qs.filter(menu__menu_isEnabled=True).filter(post_isEnabled=True)
        
        except Post.DoesNotExist as e:
            qs = Post.objects.none()
        
        return qs

    # override
    def get_context_data(self, **kwargs):
        context = TaggedObjectList.get_context_data(self, **kwargs)
        context["tagName"] = self.tag
        return context


# Tags Cloud
class TagTV(TemplateView):
    template_name = "post/post_list_via_tag.html"

    def get_context_data(self, **kwargs):
        context = TemplateView.get_context_data(self, **kwargs)
        context["tagName"] = ""
        return context



