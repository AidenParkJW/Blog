var UT =
{
    isArray : function(object) 
    {
        return Array.isArray(object);
    },

    isString : function(object)
    {
        return "string" === typeof object;
    },

    isBoolean : function(object)
    {
        return "boolean" === typeof object;
    },

    isNumber : function(object)
    {
        return "number" === typeof object;
    },

    isFunction : function(object)
    {
        return "function" === typeof object;
    },

    isObject : function(object)
    {
        return object !== null && "object" === typeof object;
    },

    isDate: function(object)
    {
        return UT.isObject(object) && typeof object.getTime === "function";
    },
    
    isFile : function(object)
    {
        return object !== null && "[object File]" === object.toString();
    },
    
    isEmpty: function(object)
    {
        return object === null || "undefined" === typeof object || (UT.isObject(object) && !Object.keys(object).length && !UT.isDate(object)) || (UT.isString(object) && object.trim() === "") || (UT.isArray(object) && object.length === 0);
    },
    
    isNotEmpty : function(object)
    {
        return !UT.isEmpty(object);
    },
    
    nvl : function(object, defaultValue)
    {
        if (UT.isEmpty(object))
        {
            return defaultValue;
        }

        return object;
    },
    
    toNumber : function(value)
    {
        if (UT.isString(value))
        {
            value = value.replace(/[\,]/g, "");
        }
        
        return isNaN(value) ? 0 : Number(value);
    },
    
    hasItem : function(array, item)
    {
        if (UT.isArray(array) && UT.isNotEmpty(item))
        {
            return array.indexOf(item) > -1;
        }
        
        return false;
    },
    
    getCsrftoken : function()
    {
        return UT.getCookie("csrftoken");
    },
    
    setCookie : function(cname, cvalue, exdays)
    {
        var d = new Date();
        
        d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
        
        var expires = "expires="+d.toUTCString();
        
        document.cookie = cname + "=" + encodeURIComponent(cvalue) + ";" + expires + ";path=/";
    },
    
    getCookie : function(cname)
    {
        var name = cname + "=";
        var ca = document.cookie.split(';');
        
        for (var i = 0; i < ca.length; i++)
        {
            var c = ca[i];
            
            while (c.charAt(0) == " ")
            {
                c = c.substring(1);
            }
            
            if (c.indexOf(name) == 0)
            {
                return decodeURIComponent(c.substring(name.length, c.length));
            }
        }
        
        return "";
    },
    
    stringFormat : function()
    {
        var args = arguments;
        
        var src = args[0];
        
        for (var i = 1; i < args.length; i++)
        {
            var _word = UT.nvl(args[i], "");
            var _patt = new RegExp("\\{" + (i - 1) + "\\}", "g");
            
            src = src.replace(_patt, _word);
        }
        
        return src;
    },

    formatedFileSize : function(fileSize)
    {
        var _unit = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
        var _fileSize = UT.toNumber(fileSize);
        var _i = 0;
            
        if (fileSize > 0)
        {
            _fileSize = fileSize / Math.pow(1024, (_i = Math.floor(Math.log(1024, fileSize))));
        }
        
        return _fileSize.toFixed(2) + " " + _unit[_i];
    },
    
    ajax : function(type, url, data, callbackSuccess, callbackError)
    {
        if (UT.isEmpty(url)) return;
        
        if (!UT.isFunction(callbackError))
        {
            callbackError = function(xhr, status, error)
            {
                console.log(status + " : " + error);
            }
        }
        
        $.ajax({ type: type
               , url: url
               , data: data
               , dataType: "json"
               , headers: {"X-CSRFToken": UT.getCsrftoken()}
               , success: callbackSuccess
               , error: callbackError
               });
    },
}

Math.log = (function()
{
    var log = Math.log;
    return function(base, n)
    {
        return log(n) / (base ? log(base) : 1);
    };
})();
