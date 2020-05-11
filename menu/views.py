from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from menu.models import Menu


# Create your ajax views here.
class MenuAV():
    
    @staticmethod
    @require_http_methods(["POST", "GET"])
    def load(request, **kwargs):
        if request.is_ajax():
            if request.user.is_superuser: 
                # retrieve all menu
                _menuList = [menu.getMenuDict() for menu in Menu.objects.annotate(post_cnt=Count("menu_post"))]
            else:
                # retrieve only enabled menu & post
                _menuList = [menu.getMenuDict() for menu in Menu.objects.annotate(post_cnt=Count("menu_post", filter=Q(menu_post__post_isEnabled=True))).filter(menu_isEnabled=True)]
        
        else:
            _menuList = None
            
        #print(_menuList)
        #safe=False -> for allow non Dict type.
        #json_dumps_params={"ensure_ascii": False} -> for unicode
        return JsonResponse(_menuList, safe=False, json_dumps_params={"ensure_ascii": False})
    