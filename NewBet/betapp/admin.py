from django.contrib import admin
from .models import *


admin.site.register(Competition)
admin.site.register(Team)
admin.site.register(Fixture)
admin.site.register(AppUser)
admin.site.register(Bet)