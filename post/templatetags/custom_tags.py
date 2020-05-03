from django import template
from datetime import date
from django.db.models import Q
from menu.models import Menu

register = template.Library()

@register.filter(name="range", is_safe=False)
def _range(_min, args=None):
    _max, _step = None, None
    if args:
        if not isinstance(args, int):
            _max, _step = map(int, args.split(','))
        else:
            _max = args
    args = filter(None, (_min, _max, _step))
    return range(*args)


@register.filter(is_safe=False)
def sub(value, arg):
    """Substract the arg to the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except Exception:
            return ""

@register.filter(is_safe=False)
def mul(value, arg):
    """Multiply the arg to the value."""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        try:
            return value * arg
        except Exception:
            return ""


@register.filter(is_safe=False)
def div(value, arg):
    """Divide the arg to the value."""
    try:
        return int(value) / int(arg)
    except (ValueError, TypeError):
        try:
            return value / arg
        except Exception:
            return ""
        

@register.simple_tag
def today():
    return date.today().strftime("%Y.%m.%d")

@register.simple_tag
def getPostFlagStyle(post_crte_dt, post_mdfy_dt):
    _today = date.today()
    _cday = post_crte_dt.date()
    _mday = post_mdfy_dt.date()
    _styleClass = ""
    
    if _cday == _mday:
        if (_today - _cday).days <= 7:
            _styleClass = "postNew"
    else:
        if (_today - _mday).days <= 7:
            _styleClass = "postUpd"
            
    return _styleClass

@register.simple_tag
def replace(value, old, new):
    return value.replace(old, new)

@register.simple_tag(takes_context=True)
def getCookies(context, cookie_name):
    request = context["request"]
    cookie_value = request.COOKIES.get(cookie_name, "") # I use blank as default value
    return cookie_value

@register.simple_tag(takes_context=True)
def getMenuPath(context):
    _menuPath = ""
    request = context["request"]
    
    try:
        if "menu_paths" in context:
            _menuPath = context["menu_paths"]
        else:
            _menuPath = Menu.objects.get(menu_url=request.path).getMenuPath()
    except Menu.DoesNotExist as e:
        pass

    return _menuPath

