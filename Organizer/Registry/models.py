from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator

class storeData(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, default = "", verbose_name = "Student Name")
    
    phone_regex = RegexValidator(regex = r'^[0-9]{10}$', message = "Phone number must be of the form: 9876543210.")
    phone_number = models.CharField(validators = [phone_regex], max_length=11, verbose_name = "Phone Number")
    
    password = models.CharField(max_length = 30, verbose_name = "Password")
    
    no_of_class_attended = models.IntegerField(default = 0)
    last_class_attended = models.DateTimeField(auto_now = True)
    
    fee_status = models.BooleanField(default = False)
    validated = models.BooleanField(default = False)
    
    is_superuser = models.BooleanField(default = False)
    is_logged_in = models.BooleanField(default = False, verbose_name = "Logged in status")
    '''
    def is_logged_in(self):
        return self.is_logged_in

    def is_superuser(self):
        return self.is_superuser
    '''

class Message(models.Model):

    message = models.CharField(max_length = 3000, verbose_name = "Message: ")
    datePosted = models.DateTimeField(auto_now_add = True, verbose_name = "Date Posted: ")
    allowedUsers = models.CharField(max_length = 1000, verbose_name = 'Allowed Users: ')

    def __str__(self):
        return self.message[:15]+'...'
        
    class Meta:
        ordering = ('-datePosted', )
