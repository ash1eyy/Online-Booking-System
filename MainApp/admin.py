from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# Register your models here.
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Tenant)
admin.site.register(Owner)
admin.site.register(Resource)
admin.site.register(LeasingRequest)
admin.site.register(Report)
admin.site.register(Announcement)