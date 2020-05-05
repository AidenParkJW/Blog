from __future__ import unicode_literals

import re

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Menu(MPTTModel):
    menu_uid        = models.AutoField("Menu UID", primary_key=True)
    menu_name       = models.CharField("Menu Name", max_length=80)
    menu_desc       = models.CharField("Menu Description", max_length=200, null=True, blank=True)
    menu_url        = models.CharField("Menu URL", max_length=256, null=True, blank=True)
    menu_sort_order = models.PositiveSmallIntegerField("Sort Order Number", default=1)
    menu_isEnabled  = models.BooleanField("Enabled", default=True)
    parent_menu     = TreeForeignKey("self", on_delete=models.PROTECT , related_name="menu_menu", db_column="menu_up_uid", db_index=True, null=True, blank=True, verbose_name="Parent Menu UID")
    site            = models.ForeignKey(Site, on_delete=models.PROTECT, related_name="site_menu", db_column="site_id", db_index=True, default=Site, verbose_name="Site")
    menu_crte_user  = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_menu_creator", db_column="menu_crte_user_id", default=User, editable=False, verbose_name="Creator")
    menu_crte_dt    = models.DateTimeField("Created DateTime", auto_now_add=True)
    menu_mdfy_user  = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_menu_modifier", db_column="menu_mdfy_user_id", default=User, editable=False, verbose_name="Modifier")
    menu_mdfy_dt    = models.DateTimeField("Modified DateTime", auto_now=True)

    class Meta:
        verbose_name        = "menu"
        verbose_name_plural = "menus"
        db_table            = "blog_menu"
        #ordering            = ["menu_sort_order"]
    
    class MPTTMeta:
        parent_attr = "parent_menu"
        order_insertion_by = ["menu_sort_order"]
        pass
    
    def getMenuPath(self):
        try:
            ancestors = self.get_ancestors(include_self=True)
        except:
            ancestors = list()
        else:
            menu_list = []
            
            for m in ancestors:
                if m.menu_url is not None:
                    menu_list.append("<a href='{}'>{}</a>".format(m.menu_url, m.menu_name))
                else:
                    menu_list.append("{}".format(m.menu_name))
        
        return " › ".join(menu_list)
    
    def getMenuDict(self):
        _dict = {}
        _dict["menu_name"] = "{} ({})".format(self.menu_name, self.post_cnt) if self.menu_url is not None and re.search(r"^/post/\d+/$", self.menu_url) else "{}".format(self.menu_name)
        _dict["menu_url"] = self.menu_url
        _dict["is_leaf"] = self.is_leaf_node()
        _dict["level"] = self.get_level()
        #print(_dict)
        return _dict
    
    def __str__(self):
        return self.menu_name


