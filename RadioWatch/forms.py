from django import forms
from django.contrib.auth.models import User

class UserSignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_password2(self):
        # Check if the two passwords match
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("The two password fields must match.")
        return password2

    def save(self, commit=True):
        # Save the user and hash the password
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # Set the hashed password
        if commit:
            user.save()  # Save the user to the database
        return user
