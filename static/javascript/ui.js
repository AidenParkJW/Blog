var UI =
{
    loadHistory : function()
    {
        _history = /(\[.+\])/.exec(UT.getCookie("history"));
        
        $("#history").empty();
        
        if (UT.isNotEmpty(_history))
        {
            _postHistory = JSON.parse(_history[1]);
            
            _postHistory.forEach(function(data, index, array)
            {
                var _div = document.createElement("div");
                _div.className = "historyTitle";
                var _a = document.createElement("a");
                _a.href = data.url;
                _a.title = data.title;
                _a.appendChild(document.createTextNode("● " + data.title));
                _div.appendChild(_a);
                
                var _del = document.createElement("div");
                _del.className = "historyDel";
                _del.appendChild(document.createTextNode("×"));
                _del.onclick = function()
                {
                    _postHistory.splice(index, 1);
                    UT.setCookie("history", JSON.stringify(_postHistory), 30);
                    UI.loadHistory();
                }
                _div.appendChild(_del);
                
                $("#history").append(_div);
            });
        }
    },
        
    switchMenu : function()
    {
        var _isOpenedMenu = UT.getCookie("isOpenedMenu");
        
        if (_isOpenedMenu == "true")
        {
            // close
            UT.setCookie("isOpenedMenu", false, 1);
            UI.closeMenu();
        }
        else
        {
            // open
            UT.setCookie("isOpenedMenu", true, 1);
            UI.openMenu();
        }
        
        // for reset line-numbers in code sample of post
        setTimeout(function()
        {
            // Works great in Chrome and FF but didn't work in IE11 and other old browsers.
            //window.dispatchEvent(new Event("resize"));
            
            // for IE and other old browsers
            var event = document.createEvent("HTMLEvents");
            event.initEvent("resize", true, false);
            window.dispatchEvent(event);
        }, 500);
    },

    autoOpenMenu : function()
    {
        var _isOpenedMenu = UT.getCookie("isOpenedMenu");

        if (_isOpenedMenu == "true")
        {
            UI.openMenu();
        }
    },
    
    openMenu : function()
    {
        var _menuNavi = document.getElementById("menuNavi");
        var _content = document.getElementById("content");
        _content.classList.add("shrink");
        
        // when display is block, animation work. 
        setTimeout(function()
        {
            _menuNavi.classList.add("menuNaviOpen");
        }, 500);
        
        // call ajax
        UT.ajax("POST", "/menu/load/", null,
                function(result, status, xhr)
                {
                    // last objects remove
                    $("#menuTree").empty();
                    
                    _menuList = result;
                    _menuList.forEach(function(data, index, array)
                    {
                        var _className = data.level == 0 ? "menuLvl01" : "menuLvl02";
                        var _div = document.createElement("div");
                        var _text = document.createTextNode(data.menu_name);
                        
                        _div.className = _className;
                        
                        if (UT.isNotEmpty(data.menu_url))
                        {
                            var _a = document.createElement("a");
                            _a.href = data.menu_url;
                            _a.appendChild(_text);
                            _div.appendChild(_a);
                        }
                        else
                        {
                            var _span = document.createElement("span");
                            _span.appendChild(_text);
                            _div.appendChild(_span);
                        }
                        
                        $("#menuTree").append(_div);
                        
                        // Adding margin between each different level menu.
                        if (UT.isNotEmpty(array[index + 1]) && data.level > array[index + 1].level)
                        {
                            var _gap = document.createElement("div");
                            _gap.className = "space-h10";
                            $("#menuTree").append(_gap);
                        }
                    });
                });
    },
    
    closeMenu : function()
    {
        var _menuNavi = document.getElementById("menuNavi");
        var _content = document.getElementById("content");
        _menuNavi.classList.remove("menuNaviOpen");
        
        // work, after animation
        setTimeout(function()
        {
            _content.classList.remove("shrink");
        }, 500);
    },
    
    switchPostStyle : function(path, value)
    {
        UT.setCookie(path, value, 1);
        //location.reload();
        location.href=".";
    },
    
    movePage : function(pageNo)
    {
        var _form = document.getElementById("postSearchForm");
        
        if (_form)
        {
            _form.action = _form.action + "?page=" + pageNo;
            _form.submit();
        }
        else
        {
            location.href = location.pathname + "?page=" + pageNo;
        }
    },

    makeAuthUrlWithNext : function(url)
    {
        // make social login url with call back url
        var _pathname = location.pathname;
        var _search = location.search;  // this is login required url
        
        // If it came from a login required, go to the current screen.
        if (UT.isNotEmpty(_search))
        {
            // The url has a callback url by default. so then replace
            url = url.substring(0, url.indexOf("?")) + _search;
            
            // don't need popup
            location.href = url;
            return null;
        }
        // If it is a simple login, popup
        else
        {
            return url;
        }
    },
    
    openAuthKakao : function(url)
    {
        url = UI.makeAuthUrlWithNext(url);

        if (UT.isNotEmpty(url))
        {
            var _pop = window.open(url, "Login with Kakao", "width=500,height=650");
            
            var _width   = screen.width;
            var _height  = screen.height;
            
            var _left = _width / 2 - 500 / 2;
            var _top  = _height / 2 - 600 / 2;

            _pop.moveTo(_left, _top);
        }
    },
    
    openAuthNaver : function(url)
    {
        url = UI.makeAuthUrlWithNext(url);
        
        if (UT.isNotEmpty(url))
        {
            var _pop = window.open(url, "Login with NAVER", "width=500,height=650");
            
            var _width   = screen.width;
            var _height  = screen.height;
            
            var _left = _width / 2 - 500 / 2;
            var _top  = _height / 2 - 600 / 2;

            _pop.moveTo(_left, _top);
        }
    },
    
    openAuthGoogle : function(url)
    {
        url = UI.makeAuthUrlWithNext(url);
        
        if (UT.isNotEmpty(url))
        {
            var _pop = window.open(url, "Login with Google+", "width=400,height=650");
            
            var _width   = screen.width;
            var _height  = screen.height;
            
            var _left = _width / 2 - 400 / 2;
            var _top  = _height / 2 - 600 / 2;

            _pop.moveTo(_left, _top);
        }
    },
    
    getForm : function(element)
    {
        if (element != null && element.parentElement != null)
        {
            if (element.parentElement.tagName == "FORM")
            {
                return element.parentElement;
            }
            else
            {
                return UI.getForm(element.parentElement);
            }
        }
        else
        {
            return null;
        }
    }
}