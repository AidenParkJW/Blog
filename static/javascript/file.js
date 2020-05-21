var AttFile = (function() {
    var _validExts = [];                // ["jpg", "pdf"...], [] is allow all extensions.
    var _limitSize = 1024 * 1024 * 100; // unit is byte , 0 is unlimited size.
    
    var _stdFiles = [];
    var _delFiles = [];
    var _insFiles = [];
    
    var _changeFileCallback = null;
    var _uploadPrgsCallback = null;
    var _uploadCmptCallback = null;
    
    return {
        setValidExts : function(validExts) { _validExts = validExts },
        setLimitSize : function(limitSize) { _limitSize = limitSize },
        
        getStdFiles : function() { return _stdFiles; },
        getDelFiles : function() { return _delFiles; },
        getInsFiles : function() { return _insFiles; },
        
        addListenerChangeFile : function(callback) { _changeFileCallback = callback; },
        addListenerUploadPrgs : function(callback) { _uploadPrgsCallback = callback; },
        addListeneruploadCmpt : function(callback) { _uploadCmptCallback = callback; },
        
        add : function(file)
        {
            var _stdIndex = Array.prototype.indexOf.call(_stdFiles, file);
            var _rtn;
            
            if (_stdIndex == -1)
            {
                _rtn = Array.prototype.push.call(_insFiles, file);
            }
            
            if (UT.isFunction(_changeFileCallback))
            {
                _changeFileCallback.call();
            }
            
            return _rtn;
        },
        
        remove : function(file)
        {
            var _stdIndex = Array.prototype.indexOf.call(_stdFiles, file);
            var _delIndex = Array.prototype.indexOf.call(_delFiles, file);
            var _insIndex = Array.prototype.indexOf.call(_insFiles, file);
            var _rtn;
            
            if (_stdIndex > -1)
            {
                if (_delIndex == -1)
                {
                    _rtn = Array.prototype.push.call(_delFiles, file);
                }
                else
                {
                    _rtn = Array.prototype.splice.call(_delFiles, _delIndex, 1);
                }
            }
            
            if (_insIndex > -1)
            {
                _rtn = Array.prototype.splice.call(_insFiles, _insIndex, 1);
            }
            
            if (UT.isFunction(_changeFileCallback))
            {
                _changeFileCallback.call();
            }
            
            return _rtn;
        },
        
        isRemoved : function(file)
        {
            return _delFiles.indexOf(file) > -1;
        },
        
        status : function()
        {
            var _fileCount = 0
            var _totalSize = 0;
            
            _stdFiles.forEach(function(file, index, array)
            {
                if (_delFiles.indexOf(file) == -1)
                {
                    _fileCount += 1;
                    _totalSize += file.size;
                }
            });
            
            _insFiles.forEach(function(file, index, array)
            {
                _fileCount += 1;
                _totalSize += file.size;
            });
            
            return UT.stringFormat("{0} of {1} files", UT.formatedFileSize(_totalSize), _fileCount);
        },

        isEmpty : function()
        {
            return UT.isEmpty(_stdFiles) && UT.isEmpty(_insFiles);
        },
        
        validate : function()
        {
            var _rtnVal = {};
            _rtnVal.isValid = true;
            _rtnVal.message = null;
            _totalSize = 0;
            
            for (var i in _insFiles)
            {
                _insFile = _insFiles[i];
                
                var _ext = _insFile.name.split(".")[1];
                
                if (UT.isNotEmpty(_ext))
                {
                    if (UT.isNotEmpty(_validExts) && !UT.hasItem(_validExts, _ext))
                    {
                        _rtnVal.isValid = false;
                        _rtnVal.message = UT.stringFormat("Invalid file type ({0}).", _ext);
                        break;
                    }
                }
                
                _totalSize += _insFile.size;
                if (_limitSize > 0 && _totalSize > _limitSize)
                {
                    _rtnVal.isValid = false;
                    _rtnVal.message = UT.stringFormat("Upload File size exceeded (limit {0}).", UT.formatedFileSize(_limitSize));
                    break;
                }
            }
            
            return _rtnVal;
        },
        
        load : function(content_type, object_uid, callback)
        {
            var _data = {};
            _data.content_type  = content_type;
            _data.object_uid    = object_uid;
            
            UT.ajax("POST", "/attFile/load/", _data,
                    function(result, status, xhr)
                    {
                        _stdFiles = result;
                        
                        if (UT.isFunction(callback))
                        {
                            callback.call(null, _stdFiles);
                        }
                    });

            var _form = UI.getForm(document.querySelector("[type=file]"));
            if (_form != null)
            {
                _form.addEventListener("submit", function(event)
                {
                    event.preventDefault();
                    event.stopPropagation();
                    
                    _form.removeEventListener(event.type, arguments.callee);
                    
                    var validatorTextArea = function()
                    {
                        var _textArea = _form.querySelector("textarea");
                        if (_textArea != null && _textArea.style.display == "none")
                        {
                            if (UT.isEmpty(tinyMCE.get(_textArea.id).getContent()))
                            {
                                alert("Content field is required.");
                                return false;
                            }
                        }
                        return true;
                    }
                    
                    if (_form.checkValidity() && validatorTextArea())
                    {
                        this.upload();
                    }
                }.bind(this));
                
                _uploadCmptCallback = function()
                {
                    _form.submit();
                }
            }
        },
        
        upload : function()
        {
            if (UT.isNotEmpty(_insFiles) || UT.isNotEmpty(_delFiles))
            {
                var _rtnVal = this.validate();
                
                if (_rtnVal.isValid)
                {
                    var formData = new FormData();
                    
                    _insFiles.forEach(function(file, index, array)
                    {
                        formData.append("insFiles", file);
                    });
                    
                    _delFiles.forEach(function(file, index, array)
                    {
                        formData.append("delFiles", file.uid);
                    });
                    
                    $.ajax( { type          : "POST"
                            , url           : "/attFile/upload/"
                            , data          : formData
                            , contentType   : false
                            , processData   : false
                            , dataType      : "json"
                            , headers       : {"X-CSRFToken": UT.getCsrftoken()}
                            , xhr           :   function() 
                                                {
                                                    // XMLHttpRequest 재정의 가능
                                                    var xhr = $.ajaxSettings.xhr();
                                                    xhr.upload.onprogress = function(event)
                                                    { 
                                                        // progress 이벤트 리스너 추가
                                                        var percent = event.loaded * 100 / event.total;
    
                                                        if (UT.isFunction(_uploadPrgsCallback))
                                                        {
                                                            _uploadPrgsCallback.call(this, percent);
                                                        }
                                                    };
                                                    return xhr;
                                                }
                            
                            , success       :   function(result, status, xhr)
                                                {
                                                    var _result = result.result;
                                                    
                                                    //console.log(_result.status + " : " + _result.message + " : " + status + " : " + xhr);
                                                    
                                                    // if success
                                                    if (_result.status)
                                                    {
                                                        if (UT.isNotEmpty(_result.message))
                                                        {
                                                            alert(_result.message);
                                                        }
                                                        else
                                                        {
                                                            if (UT.isFunction(_uploadCmptCallback))
                                                            {
                                                                _uploadCmptCallback.call();
                                                            }
                                                        }
                                                    }
                                                    
                                                    // if fail
                                                    if (!_result.status)
                                                    {
                                                        alert(_result.message);
                                                        location.href = "/";
                                                    }
                                                }
                            
                             , error        :   function(xhr, status, error)
                                                {
                                                    console.log(status + " : " + error);
                                                }
                             
                             , complete     :   function(xhr, status)
                                                {
                                                    //console.log(status + " : " + xhr);
                                                }
                    });
                }
                else
                {
                    alert(_rtnVal.message);
                }
            }
            else
            {
                _uploadCmptCallback();
            }
        },
        
        download : function(file)
        {
            var xhr = new XMLHttpRequest();
            xhr.onreadystatechange = function()
            {
                // https://www.w3schools.com/js/js_ajax_http.asp
                //console.log(this.readyState + ":" + this.status + ":" + this.statusText);
                
                if (this.readyState == 4 && this.status == 200)
                {
                    var _contentType = xhr.getResponseHeader("content-Type");
                    var _blob = new Blob([this.response], {type:_contentType});
                    var _a = document.createElement("a");
                    _a.href = window.URL.createObjectURL(_blob);
                    _a.download = file.name;
                    _a.click();
                }
                
                if (this.readyState == 4 && this.status == 500)
                {
                    alert("File not found.");
                }
            };

            xhr.open("GET", "/attFile/download/" + encodeURIComponent(file.uid) + "/", true);
            xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8");
            xhr.responseType = "blob";
            xhr.send();
        },
    }
})();