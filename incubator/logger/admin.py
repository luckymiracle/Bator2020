from django.contrib import admin

# from .models import DHT, incubation, Rotation, Email, RHT
import models as mod

admin.site.register(mod.DHT)
admin.site.register(mod.incubation)
admin.site.register(mod.Rotation)
admin.site.register(mod.Email)
admin.site.register(mod.RHT)
admin.site.register(mod.Recipients)
