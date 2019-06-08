from django.contrib import admin
from .models import Message, storeData, FileUpload

#admin.site.register(Message)
@admin.register(FileUpload)
class PostAdmin(admin.ModelAdmin):
    list_display = ('description', 'uploadedFile', 'upload_time')
    ordering = ('upload_time', )
    search_fields = ('description', 'upload_time')

@admin.register(Message)
class PostAdmin(admin.ModelAdmin):
    list_display = ('message', 'datePosted', 'allowedUsers')
    ordering = ('-datePosted', )
    search_fields = ('messages',)

@admin.register(storeData)
class PostAdmin(admin.ModelAdmin):
    list_display = ('username', 'phone_number', 'no_of_class_attended', 'fee_status', 'validated', 'is_logged_in',)
    ordering = ('username', )
    search_fields = ('username', 'phone_number', 'fee_status', 'validated')