var Slider = (function() {
    var _slide;
    var _thumbWidth = 0;
    var _thumbImgs = [];
    var _slideImgs = [];
    var _index = 0;
    
    return {
        load : function(content_type, object_uid, callback)
        {
            var _data = {};
            _data.content_type  = content_type;
            _data.object_uid    = object_uid;
            _data.onlyImage     = "Y";
            
            UT.ajax("POST", "/attFile/load/", _data,
                    function(result, status, xhr)
                    {
                        if (UT.isFunction(callback))
                        {
                            callback.call(null, result);
                            this.init();
                        }
                    }.bind(this));
        },
        
        init : function()
        {
            _slide = document.getElementById("slide");
            
            _thumbImgs = [].slice.call(document.getElementsByClassName("thumbImg"));
            _slideImgs = [].slice.call(document.getElementsByClassName("slideImg"));
            
            if (_thumbImgs.length == 0)
            {
                _slide.style.display = "none";
            }
            else
            {
                _thumbWidth = _thumbImgs[0].getBoundingClientRect().width + 1;  // margin 1px
                this.moveImg(0);
            }
        },
        
        calcSize : function()
        {
            var _rect = _slide.getBoundingClientRect();
            
            return Math.floor(_rect.width / _thumbWidth);
        },
        
        getThumbs : function()
        {
            return _thumbImgs;
        },
        
        prevImg : function()
        {
            this.moveImg(-1);
        },
        
        nextImg : function()
        {
            this.moveImg(+1);
        },
        
        moveImg : function(n)
        {
            _index += n;
            
            if (_index > _thumbImgs.length - 1) { _index = 0 }
            if (_index < 0) { _index = _thumbImgs.length - 1 }
            
            this.display();
        },
        
        view : function(thumb)
        {
            _index = _thumbImgs.indexOf(thumb);
            
            this.display();
        },
        
        display : function()
        {
            _listSize = this.calcSize();
            
            // Display the same group thumbnail images.
            _thumbImgs.forEach(function(_thumbImg, index, array)
            {
                if (Math.floor(index / _listSize) == Math.floor(_index / _listSize))
                {
                    _thumbImg.style.display = "flex";
                }
                else
                {
                    _thumbImg.style.display = "none";
                }
                
                _thumbImg.querySelector("img").classList.remove("active");
            });
            
            // Reset display property of slide images.
            _slideImgs.forEach(function(_slideImg, index, array)
            {
                _slideImg.style.display = "none";
            });
            
            // Active selected thumbnail image and Show selected image
            if (_thumbImgs.length > 0)
            {
                _thumbImgs[_index].querySelector("img").classList.add("active");
                _slideImgs[_index].style.display = "block";
                _slideImgs[_index].querySelector("[class=num]").innerText = UT.stringFormat("{0} / {1}", (_index + 1), _slideImgs.length);
            }
        },
    }
})();
