from django.contrib import admin
from users.models import *


admin.site.register(User)
admin.site.register(Device)
admin.site.register(Activity)
