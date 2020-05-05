from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.forms.widgets import TextInput
from django.utils.translation import gettext_lazy as _

from post.models import Post


class PostSearchForm(forms.Form):
    search_word = forms.CharField(label=False, required=True, max_length=20, widget=forms.TextInput(attrs={"placeholder":"Search.."}))


class PostForm(forms.ModelForm):
    
    class Meta:
        model = Post
        fields = ["post_title", "post_content", "post_tag", "post_isEnabled"]
        
        labels = {
            "post_title": _("Title"),
            #"post_slug": _("Slug"),
            "post_content": _("Content"),
            "post_tag": _("Tags"),
            "post_isEnabled": _("Enabled"),
        }
        
        widgets = {
            #"post_title": TextInput(attrs={"required": True}),
            #"post_slug": TextInput(attrs={"hidden": True, "value": "auto-filling-do-not-input"}),
            "post_tag": TextInput(attrs={"placeholder": "ex) Tech, Music"}),
        }

    # override
    def __init__(self, *args, **kwargs):
        #print(inspect.stack()[0][3])
        super().__init__(*args, **kwargs)
        request = kwargs["initial"]["request"]  # came from views
        
        _post_content = self.fields.get("post_content")
        _post_content.required = False  # because of tinyMCE Editor, it makes non-visible field that can't focus.
        '''
        Below script is correct but not working. because "MinLengthValidator" can't check null or blank.
        so I added validation in clean function.
        '''
        _post_content.validators.append(MinLengthValidator(1, message="This field is required."))

        # if not superuser. Don't allow modification 
        if not request.user.is_superuser:
            self.fields.get("post_isEnabled").widget.attrs["onclick"] = "return false;"

    # override
    def clean(self):
        cleaned_data = forms.ModelForm.clean(self)
        
        '''
        It has no "post_content" here if it was previously invalid in validation.
        So you have to make sure you have it or not.
        '''
        if "post_content" in cleaned_data:
            _post_content = cleaned_data["post_content"]
            
            # https://docs.djangoproject.com/en/3.0/ref/models/instances/#django.db.models.Model.clean
            if _post_content is None or len(_post_content) == 0:
                # Can't use "Content" that is label of post_content.
                raise ValidationError({"post_content" : ValidationError(_("This field is required."), code="required")})
            
        return cleaned_data

