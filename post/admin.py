from django.contrib import admin
from post.models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display        = ("menu", "post_title", "post_isEnabled", "post_mdfy_user", "post_crte_dt", "post_mdfy_dt")
    list_filter         = ("post_mdfy_dt", "menu")
    search_fields       = ("post_title", "post_content")
    prepopulated_fields = {"post_slug":("post_title",)}
    raw_id_fields       = ["menu"]

    # set linked attribute name
    list_display_links = ["post_title"]
    
    fields = ["menu", "post_title", "post_slug", "post_content", "post_tag", "post_isEnabled", "post_views", ("post_crte_dt", "post_crte_user"), ("post_mdfy_dt", "post_mdfy_user")]

    # set readonly fields
    readonly_fields = ["post_views", "post_crte_user", "post_crte_dt", "post_mdfy_user", "post_mdfy_dt"]

    # set Actions
    actions = ["makeEnable", "makeDisable"]
    
    #===========================================================================
    # def getPostCrteDt(self, post):
    #     return post.post_crte_dt.strftime("%Y/%m/%d %H:%M:%S")
    # 
    # getPostCrteDt.short_description = "Created Datetime"
    # 
    # def getPostMdfyDt(self, post):
    #     return post.post_mdfy_dt.strftime("%Y/%m/%d %H:%M:%S")
    # 
    # getPostMdfyDt.short_description = "Modified Datetime"
    #===========================================================================

    # add admin action
    def makeEnable(self, request, queryset):
        updatedCnt = queryset.update(post_isEnabled=True)
        self.message_user(request, "{} cases have been enabled".format(updatedCnt))
        
    makeEnable.short_description = "Enable Post"
    
    # add admin action
    def makeDisable(self, request, queryset):
        updatedCnt = queryset.update(post_isEnabled=False)
        self.message_user(request, "{} cases have been disabled".format(updatedCnt))
        
    makeDisable.short_description = "Disable Post"
    
    # override
    # https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#modeladmin-methods
    def save_model(self, request, obj, form, change):
        # should assign user object rather than user ID
        # if not obj.post_uid: same below script
        if not change:
            obj.post_crte_user = request.user
            obj.post_mdfy_user = request.user
        else:
            obj.post_mdfy_user = request.user
        
        super().save_model(request, obj, form, change)

# below syntax is replaced by a decorator
#admin.site.register(Post, PostAdmin)