from .models import *
from django import forms

class BrotherForm(forms.ModelForm):
    class Meta:
        model=Brother
        fields = ['first_name', 'last_name', 'roster_number', 'semester_joined', 'school_status', 'brother_status',
                  'case_ID', 'birthday', 'hometown', 'phone_number', 'room_number', 'current_residence',
                  'standing_committee', 'operational_committee']

class BrotherStatusForm(forms.Form):

class PositionForm(forms.ModelForm):
    class Meta:
        model=Position
        fields = []

class ExcuseForm(forms.ModelForm):
    class Meta:
        model = Excuse
        fields = []

class PotentialNewMemberForm(forms.ModelForm):
    class Meta:
        model = PotentialNewMember
        fields = []

class ScholarshipReportForm(forms.ModelForm):
    class Meta:
        model = ScholarshipReport
        fields = []

class StudyTableEventForm(forms.ModelForm);
    class Meta:
        model = StudyTableEvent
        fields = []

class ChapterEventForm(forms.ModelForm):
    class Meta:
        model = ChapterEvent
        fields = []

class RecruitmentEventForm(forms.ModelForm):
    class Meta:
        model = RecruitmentEvent
        fields = []

class PhilanthropyEventForm(forms.ModelForm):
    class Meta:
        model = PhilanthropyEvent
        fields = []

class ServiceEventForm(forms.ModelForm):
    class Meta:
        model = ServiceEvent
        fields = []

class ExcuseResponseForm(forms.Form):