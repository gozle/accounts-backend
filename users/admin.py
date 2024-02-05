from django.contrib import admin
from users.models import *
# Register your models here.

admin.site.register(User)
admin.site.register(Email)
admin.site.register(UserSetting)
admin.site.register(Profile)
admin.site.register(City)
admin.site.register(Region)
admin.site.register(BalanceChange)
