from django.contrib import admin
from menu.models import Menu
from mptt.admin import DraggableMPTTAdmin
from django.utils.html import format_html

@admin.register(Menu)
class MenuAdmin(DraggableMPTTAdmin):
    
    # set attributes to be shown
    list_display    = ["tree_actions", "menu_uid", "getMenuName", "menu_isEnabled", "getMenuUrl", "menu_mdfy_user", "menu_crte_dt", "menu_mdfy_dt"]
    #list_display    = ["menu_uid", "menu_name", "menu_isEnabled", "menu_mdfy_dt"]
    #list_display    = ["getMenuName", "menu_mdfy_dt"]
    
    # set linked attribute name
    list_display_links = ["getMenuName"]

    # set the sort order of the fields
    fields = ["site", "menu_name", "menu_desc", "menu_url", "menu_sort_order", "menu_isEnabled", "parent_menu", ("menu_crte_dt", "menu_crte_user"), ("menu_mdfy_dt", "menu_mdfy_user")]
    
    # set readonly fields
    readonly_fields = ["menu_crte_user", "menu_crte_dt", "menu_mdfy_user", "menu_mdfy_dt"]
    
    # set Actions
    actions = ["makeEnable", "makeDisable"]
    
    # mptt_level_indent = 20
    # set formatting
    def getMenuName(self, menu):
        return format_html(
            "<div style='text-indent:{}px'>{}. {}</div>",
            menu._mpttfield("level") * self.mptt_level_indent,
            menu.menu_sort_order,
            menu.menu_name,  # Or whatever you want to put here
        )
    
    getMenuName.short_description = "Menu Name"

    def getMenuUrl(self, menu):
        _url = ""
        if menu.menu_url:
            _url = format_html("<a href='{0}' target='_blank'>{0}</a>", menu.menu_url)

        return _url

    getMenuUrl.short_description = "Menu Link"

    # Actually don't need, because below script is same settings.DATETIME_FORMAT = "Y/m/d H:i:s"
    def getMenuMdfyDt(self, menu):
        return menu.menu_mdfy_dt.strftime("%Y/%m/%d %H:%M:%S")

    getMenuMdfyDt.short_description = "Modified Datetime"

    # add admin action
    def makeEnable(self, request, queryset):
        updatedCnt = queryset.update(menu_isEnabled=True)
        self.message_user(request, "{} cases have been enabled".format(updatedCnt))
        
    makeEnable.short_description = "Enable Menu"
    
    # add admin action
    def makeDisable(self, request, queryset):
        updatedCnt = queryset.update(menu_isEnabled=False)
        self.message_user(request, "{} cases have been disabled".format(updatedCnt))
        
    makeDisable.short_description = "Disable Menu"
    
    # override
    # https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#modeladmin-methods
    def save_model(self, request, obj, form, change):
        # should assign user object rather than user ID
        # if not obj.menu_uid: same below script
        if not change:
            obj.menu_crte_user = request.user
            obj.menu_mdfy_user = request.user
        else:
            obj.menu_mdfy_user = request.user
        
        super().save_model(request, obj, form, change)

# below syntax is replaced by a decorator
# admin.site.register(Menu, MenuAdmin)