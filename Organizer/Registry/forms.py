from django import forms
from .models import storeData, FileUpload

class LoginForm(forms.Form):
    model = storeData
    username = forms.CharField(max_length = 100,)
    password = forms.CharField(widget = forms.PasswordInput,)

class SelectStudentForm(forms.Form):
    model = storeData
    choices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required = False)
    
class RegistrationForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput)
    phone_number = forms.CharField()
    
    class Meta:
        model = storeData
        fields = ('username', 'phone_number', 'password',)

class AttendanceForm(forms.Form):
    choices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required = False)

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileUpload
        fields = ('description', 'files',)