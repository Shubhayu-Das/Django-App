from django.contrib import admin
from .models import Message, storeData

#admin.site.register(Message)
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