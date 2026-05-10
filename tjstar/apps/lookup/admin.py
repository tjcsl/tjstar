from django.contrib import admin
from .models import TimeSlot, Presentation, LabDirector

# Register your models here.
admin.site.register(TimeSlot)
admin.site.register(Presentation)
admin.site.register(LabDirector)
