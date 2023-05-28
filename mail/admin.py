from django.contrib import admin
from mail.models import User, Email

# Register your models here.
admin.site.register(User)
admin.site.register(Email)

class EmailInline(admin.TabularInline):  # You can also use admin.StackedInline
    model = Email
    fk_name = 'user'
    extra = 0  # Defines the number of extra forms displayed

class UserAdmin(admin.ModelAdmin):
    inlines = [EmailInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)