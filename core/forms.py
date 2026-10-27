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
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import DeveloperProfile

User = get_user_model()

class DeveloperCreationForm(UserCreationForm):
    role = forms.ChoiceField(
        choices=DeveloperProfile.ROLE_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-white border-secondary'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'email': forms.EmailInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control bg-dark text-white border-secondary'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add dark theme classes to the auto-generated password fields
        self.fields['password1'].widget.attrs.update({'class': 'form-control bg-dark text-white border-secondary'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control bg-dark text-white border-secondary'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True # Gives them access to the Developer Console
        if commit:
            user.save()
            profile, _ = DeveloperProfile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.save()
        return user