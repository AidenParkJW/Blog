from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from attFile.models import AttFile
from menu.models import Menu


class Page(models.Model):
    page_uid        = models.AutoField("Page UID", primary_key=True)
    page_title      = models.CharField("Page Title", max_length=100)
    page_content    = models.TextField("Page Content")
    page_views      = models.PositiveIntegerField("Page Views", default=0)
    page_isEnabled  = models.BooleanField("Page enabled", default=False)
    attFile         = GenericRelation(AttFile, related_query_name="page", content_type_field="content_type_id", object_id_field="object_uid")
    menu            = models.ForeignKey(Menu, on_delete=models.PROTECT, related_name="menu_page", db_column="menu_uid", db_index=True, verbose_name="Menu")
    page_crte_user  = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_page_creator", db_column="page_crte_user_id", default=User, editable=False, verbose_name="Creator")
    page_crte_dt    = models.DateTimeField("Created DateTime", auto_now_add=True)
    page_mdfy_user  = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_page_modifier", db_column="page_mdfy_user_id", default=User, editable=False, verbose_name="Modifier")
    page_mdfy_dt    = models.DateTimeField("Modified DateTime", auto_now=True)

    class Meta:
        verbose_name        = "page"
        verbose_name_plural = "pages"
        db_table            = "blog_page"
        ordering            = ["-page_uid"]
        
    def __str__(self):
        return self.page_title
    
    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self)

    def get_create_url(self):
        return reverse("page:pageCV", kwargs={"menu_uid":self.menu.menu_uid})
    
    def get_update_url(self):
        return reverse("page:pageUV", kwargs={"page_uid":self.page_uid})

    def get_delete_url(self):
        return reverse("page:pageRV", kwargs={"page_uid":self.page_uid})
    
    def get_absolute_url(self):
        return reverse("page:pageDV", kwargs={"menu_uid":self.menu.menu_uid})
    
    
# https://docs.djangoproject.com/en/3.0/topics/signals/#module-django.dispatch
@receiver(post_save, sender=Page)
def updateIsEnabled(sender, **kwargs):
    page = kwargs.get("instance")
    if page.page_isEnabled:
        # https://docs.djangoproject.com/en/3.0/topics/db/queries/#updating-multiple-objects-at-once
        qs = Page.objects.filter(Q(menu=page.menu) & ~Q(page_uid=page.page_uid)).update(page_isEnabled=False)

