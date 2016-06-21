from django.contrib import admin
from .models import Brother, ChapterEvent, ServiceEvent, PhilanthropyEvent, RecruitmentEvent, EventExcuse, ServiceSubmission, Semester

# Register your models here.
admin.site.register(Brother)
admin.site.register(ChapterEvent)
admin.site.register(EventExcuse)
admin.site.register(ServiceEvent)
admin.site.register(PhilanthropyEvent)
admin.site.register(RecruitmentEvent)
admin.site.register(ServiceSubmission)
admin.site.register(Semester)
