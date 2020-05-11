from builtins import staticmethod
from datetime import datetime, timedelta
import os, shutil, pathlib, mimetypes

from django.conf import settings
from django.core import signing
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http.response import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods

from attFile.models import AttFile


# Create your ajax views here.
class AttFileAV():
    
    @staticmethod
    @require_http_methods(["POST"])
    def load(request, **kwargs):
        if request.is_ajax():
            # Defining GenericRelation with related_query_name set allows querying from the related object. like blow
            # AttFile.objects.filter(post__post_uid=_post.post_uid)
            # However, I did not use it here. This is because the AttFile object should not be retrieved by any specific object.
            qs = AttFile.objects.filter(content_type__pk=request.POST["content_type"], object_uid=request.POST["object_uid"])
            
            '''
            if you want to know actual file name, you can use this script 'os.path.basename(_attFile.att_file.name)'
            '''
            _attFiles = [{"uid": signing.dumps(_attFile.att_uid), "name": _attFile.att_name, "size": _attFile.att_file.size} for _attFile in qs]
        
        else:
            _attFiles = None

        #safe=False -> for allow non Dict type.
        #json_dumps_params={"ensure_ascii": False} -> for unicode
        return JsonResponse(_attFiles, safe=False, json_dumps_params={"ensure_ascii": False})
    
    
    @staticmethod
    @require_http_methods(["POST"])
    def upload(request, **kwargs):
        _result = {};
        _result["status"] = False
        _result["message"] = None
        _result["data"] = None
        
        if request.is_ajax():
            if request.user.is_active:
                # Delete garbage directory older than 1 hour from temporary directory
                for _dir in pathlib.Path(settings.UPLOAD_TEMP).iterdir():
                    if datetime.fromtimestamp(_dir.stat().st_mtime) < (datetime.now() - timedelta(hours = 1)):
                        shutil.rmtree(_dir, ignore_errors=True)
                
                # save new attached file
                _totalSize = 0
                _tempDir = os.path.join(settings.UPLOAD_TEMP, request.META.get("HTTP_X_CSRFTOKEN"))
                
                # Delete existing temporary directory
                shutil.rmtree(_tempDir, ignore_errors=True)
                _insFiles = request.FILES.getlist("insFiles")   # inMemoryFiles
                
                for _insFile in _insFiles:
                    # Getting extension of file without dot
                    _ext = os.path.splitext(_insFile.name)[1][1:].lower()
                    if not (_ext in settings.VALID_EXTENSIONS or _insFile.content_type.split("/")[0] == "image"):
                        # delete directory that contain files without no error
                        # https://docs.python.org/3/library/shutil.html#shutil.rmtree
                        shutil.rmtree(_tempDir, ignore_errors=True)
                        _result["message"] = "Invalid file type ({}).".format(_insFile.name)
                        break
                
                    _totalSize += _insFile.size
                    if _totalSize > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                        # delete directory that contain files without no error
                        # https://docs.python.org/3/library/shutil.html#shutil.rmtree
                        shutil.rmtree(_tempDir, ignore_errors=True)
                        _result["message"] = "Upload File size exceeded (limit {}MB).".format(settings.FILE_UPLOAD_MAX_MEMORY_SIZE / (1024 * 1024))
                        break
                    
                    # print(_insFile.file, _insFile.name, _insFile.size, _insFile.content_type)
                    # https://docs.djangoproject.com/en/3.0/ref/files/storage/#django.core.files.storage.Storage.save
                    default_storage.save(os.path.join(_tempDir, _insFile.name), _insFile)
                
                # if no error. delete stored attached file
                '''
                If you just delete a record, don’t need to do anything for related attached file. 
                Because related file is deleted through post_delete signals.
                '''
                if _result["message"] is None:
                    _delFiles = request.POST.getlist("delFiles")   # no inMemoryFiles
                    for _delFile in _delFiles:
                        
                        try:
                            _att_uid = signing.loads(_delFile)
                            _attFile = AttFile.objects.get(att_uid=_att_uid).delete()
                        
                        except AttFile.DoesNotExist as e:
                            pass
                
                _result["status"] = True
            
            else:
                _result["status"] = False
                _result["message"] = "Login required."
            
        else:
            _result["status"] = False
            _result["message"] = "Illegal access."
            
        return JsonResponse({"result":_result})
    
    @staticmethod
    @require_http_methods(["GET"])
    def download(request, **kwargs):
        _att_uid = signing.loads(kwargs["uid"])
        _attFile = AttFile.objects.get(att_uid=_att_uid)
        
        # https://docs.djangoproject.com/en/3.0/ref/request-response/#fileresponse-objects
        # response = FileResponse(open(_attFile.att_file.path, "rb")) # same below script
        response = FileResponse(_attFile.att_file.open("rb"))

        content_type, encoding = mimetypes.guess_type(_attFile.att_name)
        if content_type is None:
            content_type = "application/octet-stream"
            
        if encoding is not None:
            response["Content-Encoding"] = encoding
        
        response["Content-Type"] = content_type
        response["Content-Length"] = _attFile.att_file.size
        return response

    @staticmethod
    @require_http_methods(["GET"])
    def imageView(request, **kwargs):
        return AttFileAV.download(request, **kwargs)
        
    @staticmethod
    @require_http_methods(["GET"])
    def imageThumb(request, **kwargs):
        _att_uid = signing.loads(kwargs["uid"])
        _attFile = AttFile.objects.get(att_uid=_att_uid)
        
        # https://docs.djangoproject.com/en/3.0/ref/request-response/#fileresponse-objects
        response = FileResponse(open(_attFile.thumb_path, "rb"))

        content_type, encoding = mimetypes.guess_type(_attFile.att_name)
        if content_type is None:
            content_type = "application/octet-stream"
            
        if encoding is not None:
            response["Content-Encoding"] = encoding
        
        response["Content-Type"] = content_type
        #response["Content-Length"] = _attFile.att_file.size
        return response


# Views that cannot be called externally, called by Post and Page view
class AttFileNV():

    def save(self, instance):
        # If there is an attachment.
        _tempDir = os.path.join(settings.UPLOAD_TEMP, instance.request.META.get("CSRF_COOKIE"))
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
                attFile.content_object  = instance.object
                attFile.att_crte_user   = instance.request.user
                attFile.att_mdfy_user   = instance.request.user

                # With closes properly also on exceptions
                with open(_file, "rb") as fh:
                    # Get the content of the file, we also need to close the content file
                    with ContentFile(fh.read()) as _fileContent:
                        attFile.att_file.save(_file.name, _fileContent)
            
            # Delete temporary directory
            shutil.rmtree(_tempDir, ignore_errors=True)

    def rmTemp(self, instance):
        # Delete temporary directory
        _tempDir = os.path.join(settings.UPLOAD_TEMP, instance.request.META.get("CSRF_COOKIE"))
        shutil.rmtree(_tempDir, ignore_errors=True)


