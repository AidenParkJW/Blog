from __future__ import unicode_literals

from datetime import datetime
import os, shutil

from PIL import Image, ExifTags
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import signing
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse


def get_thumb(uri):
    parts = uri.split(".")
    parts.insert(-1, "thumb")
    return ".".join(parts)
    
# https://docs.djangoproject.com/en/3.0/ref/models/fields/#django.db.models.FileField.upload_to
def get_file_path(instance, filename):
    # file will be uploaded to UPLOAD_ROOT/%Y/%m/%d/<content_type>_<object_uid>/<filename>
    return "{0}/{1}/{2}_{3}/{4}".format(settings.UPLOAD_ROOT, datetime.now().strftime("%Y/%m/%d"), instance.content_type, instance.object_uid, filename)

class AttFile(models.Model):
    att_uid         = models.AutoField("Attachment File UID", primary_key=True)
    att_name        = models.CharField("Attachment File Name", max_length=256)
    att_file        = models.FileField("Attachment File", upload_to=get_file_path, max_length=512, unique=True, blank=True)
    att_isImage     = models.BooleanField("Image file whether or not", default=False)
    att_desc        = models.CharField("Attachment File Description", max_length=200, null=True, blank=True)
    # https://docs.djangoproject.com/en/3.0/ref/contrib/contenttypes/#generic-relations
    content_type    = models.ForeignKey(ContentType, on_delete=models.PROTECT, related_name="contentType_attFile", db_column="content_type_id", db_index=True, verbose_name="ContentType")
    object_uid      = models.PositiveIntegerField("Related Object UID", db_index=True)
    content_object  = GenericForeignKey("content_type", "object_uid")
    
    att_crte_user   = models.ForeignKey(User, on_delete=models.PROTECT, related_name="att_post_creator", db_column="att_crte_user_id", default=User, editable=False, verbose_name="Creator")
    att_crte_dt     = models.DateTimeField("Created DateTime", auto_now_add=True)
    att_mdfy_user   = models.ForeignKey(User, on_delete=models.PROTECT, related_name="att_post_modifier", db_column="att_mdfy_user_id", default=User, editable=False, verbose_name="Modifier")
    att_mdfy_dt     = models.DateTimeField("Modified DateTime", auto_now=True)

    class Meta:
        verbose_name        = "attFile"
        verbose_name_plural = "attFiles"
        db_table            = "blog_attFile"
        ordering            = ["att_uid"]
        
    def __str__(self):
        return self.att_name
    
    # Actuall file name
    @property
    def filename(self):
        return os.path.basename(self.att_file.name)
    
    @property
    def thumb_path(self):
        return get_thumb(self.att_file.path)
    
    @property
    def image_url(self):
        return reverse("attFile:imageView", kwargs={"uid":signing.dumps(self.att_uid)})

    @property
    def image_thumb_url(self):
        return reverse("attFile:imageThumb", kwargs={"uid":signing.dumps(self.att_uid)})
    
    
# https://docs.djangoproject.com/en/3.0/topics/signals/#module-django.dispatch
@receiver(post_save, sender=AttFile)
def createThumbnail(sender, **kwargs):
    attFile = kwargs.get("instance")
    if attFile.att_isImage and not os.path.exists(attFile.thumb_path):
        img = Image.open(attFile.att_file.path)
        
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break
        
        try:
            if "_getexif" in dir(img):
                if "items" in dir(img._getexif()):
                    exif = dict(img._getexif().items())
                    
                    if exif[orientation] == 3:
                        img = img.rotate(180, expand=True)
                        
                    elif exif[orientation] == 6:
                        img = img.rotate(270, expand=True)
                        
                    elif exif[orientation] == 8:
                        img = img.rotate(90, expand=True)
        except:
            pass
        
        #size = (512, 512)
        _w = int(img.size[0] / 8)
        _h = int(img.size[1] / 8)
        size = (_w, _h)
        img.thumbnail(size, Image.ANTIALIAS)
        img = img.convert("RGB")
        img.save(attFile.thumb_path)
        
        '''
        background = Image.new("RGB", size, (255, 255, 255, 0))
        background.paste(img, (int((size[0] -img.size[0]) / 2), int((size[1] - img.size[1]) / 2)))
        background.save(attFile.thumb_path, "JPEG")
        '''

@receiver(post_delete, sender=AttFile)
def deleteAttFile(sender, **kwargs):
    attFile = kwargs.get("instance")
    _parentDir = os.path.dirname(attFile.att_file.path)
    
    # delete image's thumbnail
    if attFile.att_isImage and os.path.exists(attFile.thumb_path):
        os.remove(attFile.thumb_path)
    
    if os.path.exists(attFile.att_file.path):
        # https://docs.djangoproject.com/en/3.0/ref/models/fields/#django.db.models.fields.files.FieldFile.delete
        attFile.att_file.delete(save=False)
    
    # if parent directory is empty. delete
    if os.path.exists(_parentDir) and not os.listdir(_parentDir):
        shutil.rmtree(_parentDir, ignore_errors=True)


