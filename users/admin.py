from django.contrib import admin
from users.models import *


admin.site.register(User)
admin.site.register(Email)
admin.site.register(UserSettings)
admin.site.register(Profile)
admin.site.register(Device)
admin.site.register(Activity)