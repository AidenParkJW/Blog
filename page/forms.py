from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _

from page.models import Page


class PageForm(forms.ModelForm):
    
    class Meta:
        model = Page
        fields = ["page_title", "page_content", "page_isEnabled"]
        
        labels = {
            "page_title": _("Title"),
            "page_content": _("Content"),
            "page_isEnabled": _("Enabled"),
        }
        
        widgets = {
            
        }
        
    # override
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = kwargs["initial"]["request"]  # came from views
        
        _page_content = self.fields.get("page_content")
        _page_content.required = False  # because of tinyMCE Editor, it makes non-visible field that can't focus.
        '''
        Below script is correct but not working. because "MinLengthValidator" can't check null or blank.
        so I added validation in clean function.
        '''
        _page_content.validators.append(MinLengthValidator(1, message=_("This field is required.")))

        # if not superuser. Don't allow modification 
        if not request.user.is_superuser:
            self.fields.get("page_isEnabled").widget.attrs["onclick"] = "return false;"

    # override
    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        
        '''
        It has no "page_content" here if it was previously invalid in validation.
        So you have to make sure you have it or not.
        '''
        if "page_content" in cleaned_data:
            _page_content = cleaned_data["page_content"]
            
            # https://docs.djangoproject.com/en/3.0/ref/models/instances/#django.db.models.Model.clean
            if _page_content is None or len(_page_content) == 0:
                # Can't use "Content" that is label of page_content.
                raise ValidationError({"page_content" : ValidationError(_("This field is required."), code="required")})
            
        return cleaned_data

