from django import forms
from .models import UserData, UploadedFile

class LoginForm(forms.Form):
    model = UserData
    phone_number = forms.CharField(max_length = 100,widget=forms.TextInput(
        attrs={
            "class": "form-fields",
            "placeholder": "Phone number",
            "required": "remember",
            "name": "phone_number"
        }
    ))
    password = forms.CharField(widget = forms.PasswordInput(
        attrs={
            "class": "form-fields",
            "placeholder": "Password",
            "required": "required",
            "name": "password"
        }
    ))

class SelectStudentForm(forms.Form):
    model = UserData
    choices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required = False)
    search_field = forms.CharField()
class RegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={
            "class": "form-fields",
            "placeholder": "Username",
            "name": 'username',
            "required": "required"
        }
    ))
    password = forms.CharField(widget = forms.PasswordInput(
        attrs={
            "class": "form-fields",
            "placeholder": "Password",
            "required": "required",
            "name": 'password'
        }
    ))
    confirm_password = forms.CharField(widget = forms.PasswordInput(
        attrs={
            "class": "form-fields",
            "placeholder": "Confirm Password",
            "required": "required",
            "name": 'password'
        }
    ))
    phone_number = forms.CharField(widget=forms.TextInput(
        attrs={
            "class": "form-fields",
            "placeholder": "Contact number",
            "required": "required",
            "name": 'phone_number'
        }
    ))

    email_address = forms.EmailField(widget=forms.EmailInput(
        attrs={
            "class": "form-fields",
            "placeholder": "Email address",
            "required": "required",
            "name": 'email_address'
        }
    ))
    CHOICE = (('1', 'First',), ('2', 'Second',))
    Batch = forms.ChoiceField(widget = forms.RadioSelect, choices = CHOICE)
    class Meta:
        model = UserData
        fields = ('username', 'phone_number', 'password',)

class AttendanceForm(forms.Form):
    choices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required = False)
    search_field = forms.CharField()
class UploadedFileForm(forms.Form):
    choices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required = False)
    search_field = forms.CharField(required = False)
    upload_file = forms.FileField(required=True, widget=forms.FileInput(
        attrs = {
            "id": "file-chooser",
            "value": "Choose File"
        }
    ))
    file_description = forms.CharField(required=True, widget=forms.TextInput(
        attrs={
            "name": "description",
            "placeholder": "File description / details",
            "id": "file-desc"
        }
    ))

    class Meta:
        model = UploadedFile
        fields = ('description', 'uploadedFile')

class ValidationForm(forms.Form):
    model = UserData
    CHOICE = [('1', 'Validate'), ('2', 'Discard')]
    choices = forms.MultipleChoiceField(widget=forms.RadioSelect, choices=CHOICE, required = False)

class FeesPaid(forms.Form):
    model = UserData
    choices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required = False)

class FileDownloadForm(forms.Form):
    model = UploadedFile
    choices = forms.ChoiceField(widget=forms.RadioSelect(), required = False)

class PhoneNumber(forms.Form):
    phone_number = forms.CharField(widget = forms.TextInput(
        attrs={
            "class": "form-fields",
            "placeholder": "Contact number",
            "required": "required",
            "name": 'phone_number'
        }
    ))
    class Meta:
        model = UserData

class DeleteStudentForm(forms.Form):
    choices = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, required = False)
    search_field = forms.CharField()
    