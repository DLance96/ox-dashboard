from .models import *
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="User")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class BrotherForm(forms.ModelForm):
    class Meta:
        model = Brother
        fields = ['first_name', 'last_name', 'roster_number', 'semester_joined', 'school_status', 'brother_status',
                  'case_ID', 'birthday', 'hometown', 'phone_number', 'room_number', "address",
                  'standing_committee', 'operational_committee']

# class BrotherStatusForm(forms.Form):


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['title', 'brother']

# class PositionChange(forms.Form):


class ExcuseForm(forms.ModelForm):
    class Meta:
        model = Excuse
        fields = ['brother', 'event', 'description']


class ExcuseResponseForm(forms.ModelForm):
    class Meta:
        model = Excuse
        fields = ['status', 'response_message']


class PotentialNewMemberForm(forms.ModelForm):
    class Meta:
        model = PotentialNewMember
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'primary_contact', 'secondary_contact',
                  'tertiary_contact']


class ScholarshipReportForm(forms.ModelForm):
    class Meta:
        model = ScholarshipReport
        fields = ['brother', 'cumulative_gpa', 'past_semester_gpa', 'scholarship_plan']


class StudyTableEventForm(forms.ModelForm):
    class Meta:
        model = StudyTableEvent
        fields = ['date', 'start_time', 'end_time']


class ChapterEventForm(forms.ModelForm):
    class Meta:
        model = ChapterEvent
        fields = ['name', 'mandatory', 'date', 'start_time', 'end_time']


class RecruitmentEventForm(forms.ModelForm):
    class Meta:
        model = RecruitmentEvent
        fields = ['name', 'date', 'start_time', 'end_time']


class PhilanthropyEventForm(forms.ModelForm):
    class Meta:
        model = PhilanthropyEvent
        fields = ['name', 'date', 'start_time', 'end_time']


class ServiceEventForm(forms.ModelForm):
    class Meta:
        model = ServiceEvent
        fields = ['name', 'date', 'start_time', 'end_time']


class AttendanceForm(forms.Form):
    present = forms.BooleanField(label="", required=False, label_suffix='')

    def __init__(self, *args, **kwargs):
        brother = kwargs.pop('brother', "")
        super(AttendanceForm, self).__init__(*args, **kwargs)

        if brother:
            self.fields['present'].label = brother


