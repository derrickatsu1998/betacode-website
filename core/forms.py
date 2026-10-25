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