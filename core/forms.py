from django import forms

class BugReportForm(forms.Form):
    title = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Brief summary of the bug'})
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Steps to reproduce the issue...'})
    )
    page_url = forms.URLField(
        required=False, 
        widget=forms.HiddenInput()
    )
    screenshot = forms.ImageField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    voice_note = forms.FileField(
        required=False, 
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'audio/*'})
    )


from django import forms
from django.contrib.auth.models import User
from .models import DeveloperProfile

class DeveloperCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    role = forms.ChoiceField(choices=DeveloperProfile.ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = True # Give them access to the console
        if commit:
            user.save()
            # Update their profile role
            profile = user.developer_profile
            profile.role = self.cleaned_data['role']
            profile.save()
        return user