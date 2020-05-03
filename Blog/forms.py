from django.contrib.auth import forms, get_user_model
import inspect

class UserProfileForm(forms.UserChangeForm):
    
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "first_name", "password"]

    # override
    def __init__(self, *args, **kwargs):
        #print(inspect.stack()[0][3])
        super().__init__(*args, **kwargs)
        
        # replace url of password change form
        password = self.fields.get("password")
        if password:
            password.help_text = password.help_text.replace("../password/", "../password/change/")
        
        username = self.fields.get("username")
        username.widget.attrs["readonly"] = True
        
        email = self.fields.get("email")
        email.widget.attrs["required"] = True
        
    # override
    def clean(self):
        #print(inspect.stack()[0][3])
        cleaned_data= forms.UserChangeForm.clean(self)
        
        # If there is an error, restore the original data
        if self.errors:
            cleaned_data["first_name"] = self.initial["first_name"]
            cleaned_data["email"] = self.initial["email"]

        return cleaned_data