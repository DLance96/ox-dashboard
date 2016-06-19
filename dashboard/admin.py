from django.contrib import admin
from .models import Brother, ChapterEvent, EventExcuse, ServiceEvent

# Register your models here.
admin.site.register(Brother)
admin.site.register(ChapterEvent)
admin.site.register(EventExcuse)
admin.site.register(ServiceEvent)