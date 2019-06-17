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
    confirm_password = forms.CharField(widget = forms.PasswordInput)
    phone_number = forms.CharField()
    CHOICE = (('1', 'First',), ('2', 'Second',))
    Batch = forms.ChoiceField(widget = forms.RadioSelect, choices = CHOICE)
    class Meta:
        model = storeData
        fields = ('username', 'phone_number', 'password',)

class AttendanceForm(forms.Form):
    choices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required = False)

class FileUploadForm(forms.ModelForm):
    choices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required = False)
    
    class Meta:
        model = FileUpload
        fields = ('description', 'uploadedFile')

class ValidationForm(forms.Form):
    model = storeData
    CHOICE = [('1', 'Validate'), ('2', 'Discard')]
    choices = forms.MultipleChoiceField(widget=forms.RadioSelect, choices=CHOICE, required = False)

class FeesPaid(forms.Form):
    model = storeData
    choices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required = False)

class FileDownloadForm(forms.Form):
    model = FileUpload
    choices = forms.ChoiceField(widget=forms.RadioSelect(), required = False)

class phoneNumber(forms.Form):
    phone_number = forms.CharField()
    class Meta:
        model = storeData