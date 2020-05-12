var Slider = (function() {
    var _slide;
    var _thumbImgs = [];
    var _slideImgs = [];
    var _index = 0;
    var _listSize = 8;
    
    return {
        init : function()
        {
            _slide = document.getElementById("slide");
            
            _thumbImgs = [].slice.call(document.getElementsByClassName("thumbImg"));
            _slideImgs = [].slice.call(document.getElementsByClassName("slideImg"));
            
            if (_thumbImgs.length ==0)
            {
                _slide.style.display = "none";
            }
            else
            {
                this.moveImg(0);
            }
        },
        
        calcSize : function()
        {
            var _rect = _slide.getBoundingClientRect();
             
            _listSize = Math.floor(_rect.width / 101);
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
            this.calcSize();
            
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
                
                _thumbImg.style.border = "0px solid #888";
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
                _thumbImgs[_index].style.border = "1px solid #888";
                _thumbImgs[_index].querySelector("img").classList.add("active");
                _slideImgs[_index].style.display = "block";
                _slideImgs[_index].querySelector("[class=num]").innerText = UT.stringFormat("{0} / {1}", (_index + 1), _slideImgs.length);
            }
        },
    }
})();
