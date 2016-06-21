from django.contrib import admin
from .models import Brother, ChapterEvent, EventExcuse, ServiceSubmission, Semester

# Register your models here.
admin.site.register(Brother)
admin.site.register(ChapterEvent)
admin.site.register(EventExcuse)
admin.site.register(ServiceSubmission)
admin.site.register(Semester)
