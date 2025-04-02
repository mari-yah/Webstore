from django import forms
from .models import UserRadioWatch
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    # Customize this form as needed
    pass

class UserRadioWatchForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = UserRadioWatch
        fields = ['user_name', 'email_id', 'password1', 'password2']

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
    
#class LoginForm(forms.Form):
    #username_or_email = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username or Email'}))
    #password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))





