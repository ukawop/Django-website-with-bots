from django.contrib import admin

from .models import Room, Message

#admin.site.register(Room)
#admin.site.register(Message)

@admin.register(Message)
class PostAdmin(admin.ModelAdmin):
    list_display = ["user"]
    save_as = True
    save_on_top = True

@admin.register(Room)
class PostAdmin(admin.ModelAdmin):
    list_display = ["name", 'user']
    prepopulated_fields = {'slug': ('name',), }
    save_as = True
    save_on_top = True