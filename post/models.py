from __future__ import unicode_literals
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.text import slugify
from tagging.fields import TagField
from menu.models import Menu
from django.contrib.contenttypes.fields import GenericRelation
from attFile.models import AttFile
from django.contrib.contenttypes.models import ContentType

class Post(models.Model):
    post_uid        = models.AutoField("Post UID", primary_key=True)
    post_title      = models.CharField("Post Title", max_length=100)
    post_slug       = models.SlugField("Post Slug", max_length=100, unique=False, allow_unicode=True, help_text="one word for title alias.")
    post_content    = models.TextField("Post Content")
    post_views      = models.PositiveIntegerField("Views", default=0)
    post_isEnabled  = models.BooleanField("Enabled", default=True)
    post_tag        = TagField()
    # https://docs.djangoproject.com/en/3.0/ref/contrib/contenttypes/#reverse-generic-relations
    # AttFile.objects.filter(post__post_uid=_post.post_uid)
    # if you delete a post that has an GenericRelation, attFile object which have a GenericForeignKey pointing at it will be deleted as well. at the same time. 
    attFile         = GenericRelation(AttFile, related_query_name="post", content_type_field="content_type_id", object_id_field="object_uid")
    menu            = models.ForeignKey(Menu, on_delete=models.PROTECT, related_name="menu_post", db_column="menu_uid", db_index=True, verbose_name="Menu")
    post_crte_user  = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_post_creator", db_column="post_crte_user_id", default=User, editable=False, verbose_name="Creator")
    post_crte_dt    = models.DateTimeField("Created DateTime", auto_now_add=True)
    post_mdfy_user  = models.ForeignKey(User, on_delete=models.PROTECT, related_name="user_post_modifier", db_column="post_mdfy_user_id", default=User, editable=False, verbose_name="Modifier")
    post_mdfy_dt    = models.DateTimeField("Modified DateTime", auto_now=True)

    class Meta:
        verbose_name        = "post"
        verbose_name_plural = "posts"
        db_table            = "blog_post"
        ordering            = ["-post_uid"]
        
    def __str__(self):
        return self.post_title
    
    @property
    def content_type(self):
        return ContentType.objects.get_for_model(self)
    
    def get_list_url(self):
        return reverse("post:postLV", kwargs={"menu_uid":self.menu.menu_uid})
    
    def get_create_url(self):
        return reverse("post:postCV", kwargs={"menu_uid":self.menu.menu_uid})
    
    def get_update_url(self):
        return reverse("post:postUV", kwargs={"post_uid":self.post_uid})

    def get_delete_url(self):
        return reverse("post:postRV", kwargs={"post_uid":self.post_uid})
    
    def get_absolute_url(self):
        return reverse("post:postDV", kwargs={"menu_uid":self.menu.menu_uid, "post_uid":self.post_uid})
    
    # not used
    def getPrevPost(self):
        try:
            _prevPost = self.get_previous_by_post_crte_dt()
        except Post.DoesNotExist:
            _prevPost = None
        
        return _prevPost
    
    # not used
    def getNextPost(self):
        try:
            _nextPost = self.get_next_by_post_crte_dt()
        except Post.DoesNotExist:
            _nextPost = None
            
        return _nextPost
    
    # override
    # https://docs.djangoproject.com/en/3.0/topics/db/models/#overriding-predefined-model-methods
    # If you use *args, **kwargs in your method definitions, you are guaranteed that your code will automatically support those arguments when they are added.
    def save(self, *args, **kwargs):
        if not self.post_uid:
            self.post_slug = slugify(self.post_title, allow_unicode=True)
        else:
            pass
        
        # all same script
        #super().save(*args, **kwargs)
        #super(Post, self).save(*args, **kwargs)
        models.Model.save(self, *args, **kwargs)

