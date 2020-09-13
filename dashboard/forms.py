from django.forms import SelectDateWidget

from .models import *
from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="User")
    password = forms.CharField(widget=forms.PasswordInput, label="Password")


class BrotherForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Retype Password"
    )

    class Meta:
        model = Brother
        fields = [
            'first_name', 'last_name', 'roster_number', 'semester_joined', 'semester_graduating',
            'school_status', 'brother_status', 'case_ID', 'major', 'minor',
            'birthday', 'hometown', 't_shirt_size', 'phone_number',
            'room_number', 'address', 'emergency_contact',
            'emergency_contact_phone_number',
        ]
        widgets = {
            'birthday': SelectDateWidget(years={1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020}),
        }


class PronounSelectorWidget(forms.MultiWidget):
    def decompress(self, value):
        if value:
            if value in [x[0] for x in self.widgets[0].choices]:
                return [value, ""]  # make it set the pulldown to choice
            else:
                return ["", value]  # keep pulldown to blank, set freetext
        return ["", ""]  # default for new object


class BrotherEditForm(forms.ModelForm):
    class Meta:
        model = Brother
        fields = [
            'first_name', 'last_name', 'pronouns', 'roster_number', 'semester_joined',
            'semester_graduating', 'school_status', 'brother_status', 'case_ID', 'major', 'minor',
            'birthday', 'hometown', 't_shirt_size', 'phone_number',
            'room_number', 'address', 'emergency_contact',
            'emergency_contact_phone_number',
        ]
        widgets = {
            'birthday': SelectDateWidget(years={1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020}),
 #           'pronouns': PronounSelectorWidget(widgets={forms.Select(choices=Brother.PronounChoices.choices), forms.TextInput})
        }

class MediaAccountForm(forms.ModelForm):
    class Meta:
        model = MediaAccount
        fields = ['media', 'username', 'profile_link']

    def __init__(self, *args, **kwargs):
        super(MediaAccountForm, self).__init__(*args, **kwargs)
        self.fields['media'].widget.attrs.update({'class': 'field'})


class MediaForm(forms.ModelForm):
    class Meta:
        model = OnlineMedia
        fields = ['name', 'icon']


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['title', 'brothers']


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
        fields = [
            'first_name', 'last_name', 'case_ID', 'phone_number',
            'primary_contact', 'secondary_contact', 'tertiary_contact', 'notes'
        ]


class StudyTableEventForm(forms.ModelForm):
    class Meta:
        model = StudyTableEvent
        fields = ['date', 'start_time', 'end_time', 'description']
        widgets = {
            'date': SelectDateWidget(),
        }


class ScholarshipEventForm(forms.ModelForm):
    class Meta:
        model = ScholarshipEvent
        fields = ['name', 'date', 'start_time', 'end_time', 'description']
        widgets = {
            'date': SelectDateWidget(),
        }


class HealthAndSafetyEventForm(forms.ModelForm):
    class Meta:
        model = HealthAndSafetyEvent
        fields = ['name', 'date', 'start_time', 'end_time', 'description']
        widgets = {
            'date': SelectDateWidget(),
        }


class ChapterEventForm(forms.ModelForm):
    class Meta:
        model = ChapterEvent
        fields = [
            'name', 'mandatory', 'date', 'start_time', 'end_time', 'minutes',
            'description',
        ]
        widgets = {
            'date': SelectDateWidget(),
        }


class CandidateEditForm(forms.ModelForm):
    class Meta:
        model = Brother
        fields = ['first_name', 'last_name', 'roster_number', 'semester_joined',
                  'school_status', 'brother_status', 'major', 'minor', 't_shirt_size',
                  'case_ID', 'birthday', 'hometown', 'phone_number',
                  'emergency_contact_phone_number', 'emergency_contact', 'room_number',
                  'address'
        ]
        widgets = {
            'birthday': SelectDateWidget(years={1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020}),
        }


class RecruitmentEventForm(forms.ModelForm):
    class Meta:
        model = RecruitmentEvent
        fields = ['name', 'rush', 'date', 'start_time', 'end_time', 'picture', 'location', 'description']
        widgets = {
            'date': SelectDateWidget(),
        }


class PhilanthropyEventForm(forms.ModelForm):
    class Meta:
        model = PhilanthropyEvent
        fields = ['name', 'date', 'start_time', 'end_time']
        widgets = {
            'date': SelectDateWidget(),
        }


class ServiceEventForm(forms.ModelForm):
    class Meta:
        model = ServiceEvent
        fields = ['name', 'date', 'start_time', 'end_time', 'description']
        widgets = {
            'date': SelectDateWidget(),
        }


class ServiceSubmissionForm(forms.ModelForm):
    class Meta:
        model = ServiceSubmission
        fields = ['name', 'date', 'hours', 'description']
        widgets = {
            'date': SelectDateWidget(),
        }


class ServiceSubmissionResponseForm(forms.ModelForm):
    class Meta:
        model = ServiceSubmission
        fields = ['status']


class CommitteeMeetingForm(forms.ModelForm):
    class Meta:
        model = CommitteeMeetingEvent
        fields = ['date', 'start_time', 'end_time', 'minutes']
        widgets = {
            'date': SelectDateWidget(),
        }


class SuppliesForm(forms.ModelForm):
    class Meta:
        model = Supplies
        fields = ['what']


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


class GPAForm(forms.Form):
    cum_GPA = forms.DecimalField(label="", max_digits=5, decimal_places=2)
    past_GPA = forms.DecimalField(label="", max_digits=5, decimal_places=2)


class PhotoForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['photo']


class MinecraftPhotoForm(forms.ModelForm):
    class Meta:
        model = MinecraftPhoto
        fields = ['photo']


class CommitteeCreateForm(forms.ModelForm):
    class Meta:
        model = Committee
        fields = ['committee', 'chair', 'meeting_interval', 'meeting_time', 'meeting_day']


class CommitteeForm(forms.Form):
    standing_committees = forms.MultipleChoiceField(
        label="", choices=Committee.STANDING_COMMITTEE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    operational_committees = forms.MultipleChoiceField(
        label="", choices=Committee.OPERATIONAL_COMMITTEE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    retype_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class SuppliesFinishForm(forms.Form):
    supplies = Supplies.objects.filter(done=False)

    choices = forms.ModelMultipleChoiceField(
        queryset=supplies,
        widget=forms.CheckboxSelectMultiple,
    )


class InHouseForm(forms.Form):
    """Selects brothers living in house"""
    in_house = Brother.objects.filter(
        brother_status='1', in_house=True
    ).order_by('user__last_name', 'user__first_name')
    not_in_house = Brother.objects.filter(
        brother_status='1', in_house=False
    ).order_by('user__last_name', 'user__first_name')

    in_house_part = forms.ModelMultipleChoiceField(
        queryset=in_house,
        widget=forms.CheckboxSelectMultiple(attrs={"checked": "checked"}),
        label="",
        required=False,
    )
    not_in_house_part = forms.ModelMultipleChoiceField(
        queryset=not_in_house,
        widget=forms.CheckboxSelectMultiple,
        label="",
        required=False,
    )


class HouseDetailsSelectForm(forms.Form):
    """Select who does house details"""
    does_details = Brother.objects.filter(
        brother_status='1', in_house=True, does_house_details=True,
    ).order_by('user__last_name', 'user__first_name')
    doesnt_do_details = Brother.objects.filter(
        brother_status='1', in_house=True, does_house_details=False,
    ).order_by('user__last_name', 'user__first_name')
    not_in_house = Brother.objects.filter(
        brother_status='1', in_house=False
    ).order_by('user__last_name', 'user__first_name')

    does_details_part = forms.ModelMultipleChoiceField(
        queryset=does_details,
        widget=forms.CheckboxSelectMultiple(attrs={"checked": "checked"}),
        label="",
        required=False,
    )
    doesnt_do_details_part = forms.ModelMultipleChoiceField(
        queryset=doesnt_do_details,
        widget=forms.CheckboxSelectMultiple,
        label="",
        required=False,
    )
    not_in_the_house = forms.ModelMultipleChoiceField(
        queryset=not_in_house,
        widget=forms.CheckboxSelectMultiple,
        label="Not in the house. Selecting these won't do anything:",
        required=False,
    )


class CreateDetailGroups(forms.Form):
    """Create detail groups for this semester"""
    semesters = Semester.objects.all()
    size = forms.IntegerField(min_value=1)
    semester = forms.ModelChoiceField(semesters)


class SelectSemester(forms.Form):
    """Select a semester"""
    semesters = Semester.objects.all().order_by('-year', '-season')
    semester = forms.ModelChoiceField(semesters)


class DeleteDetailGroup(forms.Form):
    """Allows selecting detail groups for a semester for deletion"""
    def __init__(self, *args, **kwargs):
        semester = kwargs.pop('semester')
        super(DeleteDetailGroup, self).__init__(*args, **kwargs)

        groups = DetailGroup.objects.filter(semester=semester)
        self.fields['groups'] = forms.ModelMultipleChoiceField(
            queryset=groups,
            widget=forms.CheckboxSelectMultiple,
            required=False,
        )


class SelectDetailGroups(forms.Form):
    """Select the brothers in a detail group. Dynamically creates form based
    on how many groups there are this semester"""
    def __init__(self, *args, **kwargs):
        semester = kwargs.pop('semester')
        super(SelectDetailGroups, self).__init__(*args, **kwargs)

        brothers = Brother.objects.filter(does_house_details=True).order_by(
            'user__last_name', 'user__first_name'
        )
        groups = DetailGroup.objects.filter(semester=semester)

        for i, g in enumerate(groups):
            self.fields['group_%s' % i] = forms.ModelMultipleChoiceField(
                brothers
            )
            self.fields['group_id_%s' % i] = forms.CharField(
                initial=g.pk, widget=forms.HiddenInput(),
            )

    def extract_groups(self):
        """Generator for getting the groups"""
        for name, value in self.cleaned_data.items():
            if name.startswith('group_id_'):
                num = int(name.replace('group_id_', ''))
                yield (value, self.cleaned_data['group_%s' % num])


class SelectDate(forms.Form):
    """Select a date"""
    due_date = forms.DateField()


class FinishSundayDetail(forms.Form):
    def __init__(self, *args, **kwargs):
        groupdetail = kwargs.pop('groupdetail')
        super(FinishSundayDetail, self).__init__(*args, **kwargs)

        self.fields['detail'] = forms.ModelChoiceField(
            queryset=groupdetail.details,
            widget=forms.RadioSelect,
            empty_label=None,
        )


class CalcFinesForm(forms.Form):
    max_fine = forms.IntegerField()

class BrotherMassEntryForm(forms.Form):
    brothers = forms.CharField(widget=forms.Textarea)
    brother_status = forms.ChoiceField(
        label="Brother Status", choices=Brother.BROTHER_STATUS_CHOICES
    )

    semesters = Semester.objects.all()
    semester = forms.ModelChoiceField(semesters)
