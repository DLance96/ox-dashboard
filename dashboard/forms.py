from .models import *
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="User")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class BrotherForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Retype Password")

    class Meta:
        model = Brother
        fields = ['first_name', 'last_name', 'roster_number', 'semester_joined', 'school_status', 'brother_status',
                  'case_ID', 'major', 'minor', 'birthday', 'hometown', 't_shirt_size', 'phone_number', 'room_number',
                  'address', 'emergency_contact', 'emergency_contact_phone_number']

# class BrotherStatusForm(forms.Form):


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['title', 'brother']

# class PositionChange(forms.Form):


class ExcuseForm(forms.ModelForm):
    class Meta:
        model = Excuse
        fields = ['description']


class ExcuseResponseForm(forms.ModelForm):
    class Meta:
        model = Excuse
        fields = ['status', 'response_message']


class PotentialNewMemberForm(forms.ModelForm):
    class Meta:
        model = PotentialNewMember
        fields = ['first_name', 'last_name', 'case_ID', 'phone_number', 'primary_contact', 'secondary_contact',
                  'tertiary_contact']


class ScholarshipReportForm(forms.ModelForm):
    class Meta:
        model = ScholarshipReport
        fields = ['brother', 'cumulative_gpa', 'past_semester_gpa', 'scholarship_plan', 'active']


class StudyTableEventForm(forms.ModelForm):
    class Meta:
        model = StudyTableEvent
        fields = ['date', 'start_time', 'end_time', 'notes']


class ChapterEventForm(forms.ModelForm):
    class Meta:
        model = ChapterEvent
        fields = ['name', 'mandatory', 'date', 'start_time', 'end_time', 'minutes', 'notes']


class RecruitmentEventForm(forms.ModelForm):
    class Meta:
        model = RecruitmentEvent
        fields = ['name', 'rush', 'date', 'start_time', 'end_time', 'notes']


class PhilanthropyEventForm(forms.ModelForm):
    class Meta:
        model = PhilanthropyEvent
        fields = ['name', 'date', 'start_time', 'end_time']


class ServiceEventForm(forms.ModelForm):
    class Meta:
        model = ServiceEvent
        fields = ['name', 'date', 'start_time', 'end_time', 'notes']


class ServiceSubmissionForm(forms.ModelForm):
    class Meta:
        model = ServiceSubmission
        fields = ['name', 'date', 'hours', 'description']


class BrotherAttendanceForm(forms.Form):
    present = forms.BooleanField(label="", required=False, label_suffix='')

    def __init__(self, *args, **kwargs):
        brother = kwargs.pop('brother', "")
        super(BrotherAttendanceForm, self).__init__(*args, **kwargs)

        if brother:
            self.fields['present'].label = brother


class PnmAttendanceForm(forms.Form):
    present = forms.BooleanField(label="", required=False, label_suffix='')

    def __init__(self, *args, **kwargs):
        pnm = kwargs.pop('pnm', "")
        super(PnmAttendanceForm, self).__init__(*args, **kwargs)

        if pnm:
            self.fields['present'].label = pnm


