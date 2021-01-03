from django.forms import SelectDateWidget

from .models import *
from django import forms
from django.core.validators import EMPTY_VALUES


YEAR_RANGE = range(1970, datetime.datetime.today().year+6)


class ListTextWidget(forms.TextInput):
    def __init__(self, data_list, name, *args, **kwargs):
        super(ListTextWidget, self).__init__(*args, **kwargs)
        self._name = name
        self._list = data_list
        self.attrs.update({'list':'list__%s' % self._name})

    def render(self, name, value, attrs=None, renderer=None):
        text_html = super(ListTextWidget, self).render(name, value, attrs=attrs)
        data_list = '<datalist id="list__%s" class="select">' % self._name
        for item in self._list:
            data_list += '<option value="%s">' % item
        data_list += '</datalist>'

        return text_html + data_list


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
            'birthday': SelectDateWidget(years=YEAR_RANGE),
        }


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
            'birthday': SelectDateWidget(years=YEAR_RANGE),
        }


class ClassTakenForm(forms.ModelForm):
    class Meta:
        model = Classes
        fields = [
            'department', 'number'
        ]
        help_texts = {'department': "Please only include classes you would feel comfortable tutoring others in."}
    grade = forms.CharField(label="Grade :", widget=forms.Select(choices=Grade.GradeChoices.choices))

    def __init__(self, *args, **kwargs):
        super(ClassTakenForm, self).__init__(*args, **kwargs)
        self.fields['department'].widget = ListTextWidget(data_list=Classes.objects.all().values_list('department').distinct(), name='department')


class MediaAccountForm(forms.ModelForm):
    class Meta:
        model = MediaAccount
        fields = ['media', 'username', 'profile_link']

    def __init__(self, *args, **kwargs):
        super(MediaAccountForm, self).__init__(*args, **kwargs)
        self.fields['media'].widget.attrs.update({'class': 'field'})


class CampusGroupForm(forms.ModelForm):
    class Meta:
        model = CampusGroup
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(CampusGroupForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget = ListTextWidget(data_list=CampusGroup.objects.all().distinct(), name='campus_groups')


class MediaForm(forms.ModelForm):
    class Meta:
        model = OnlineMedia
        fields = ['name', 'icon']


class PositionForm(forms.ModelForm):
    class Meta:
        model = Position
        fields = ['title', 'brothers']


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['position', 'information', 'is_officer']

    def clean(self):
        is_officer = self.cleaned_data.get('is_officer', False)
        if is_officer:
            position = self.cleaned_data.get('position', None)
            if position in EMPTY_VALUES:
                self._errors['position'] = self.error_class(['Position required for officer report'])
        return self.cleaned_data

    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['is_officer'].label = "Is officer report:"


class ReportEditForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['position', 'information', 'is_officer']

    def clean(self):
        is_officer = self.cleaned_data.get('is_officer', False)
        if is_officer:
            position = self.cleaned_data.get('position', None)
            if position in EMPTY_VALUES:
                self._errors['position'] = self.error_class(['Position required for officer report'])
        return self.cleaned_data


class ExcuseForm(forms.ModelForm):
    class Meta:
        model = Excuse
        fields = ['description']

    def clean(self):
        description = self.cleaned_data.get('description', None)
        if description == "I will not be attending because" or description in EMPTY_VALUES:
            self._errors['description'] = self.error_class(['"Please write a description"'])


class ExcuseResponseForm(forms.ModelForm):
    excuse = None

    class Meta:
        model = Excuse
        fields = ['status', 'response_message']

    def __init__(self, *args, **kwargs):
        self.excuse = kwargs.pop('excuse', None)
        super(ExcuseResponseForm, self).__init__(*args, **kwargs)

    def clean(self):
        status = self.cleaned_data.get('status', None)
        response = self.cleaned_data.get('response_message', None)
        if status == "2" and response in EMPTY_VALUES:
            self._errors['status'] = self.error_class(["Response message required for denial"])
        if status == "3" and self.excuse.event.mandatory:
            self._errors['status'] = self.error_class(["Event is mandatory cannot mark excuse not mandatory"])


class PotentialNewMemberForm(forms.ModelForm):
    class Meta:
        model = PotentialNewMember
        fields = [
            'first_name', 'last_name', 'case_ID', 'phone_number',
            'primary_contact', 'secondary_contact', 'tertiary_contact', 'notes'
        ]


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'mandatory', 'date', 'start_time', 'end_time', 'description']
        widgets = {
            'date': SelectDateWidget()
        }

    def clean(self):
        start_time = self.cleaned_data.get('start_time', None)
        end_time = self.cleaned_data.get('end_time', None)
        if end_time is not None and end_time < start_time:
            self._errors['end_time'] = self.error_class(['End time before start time'])
        return self.cleaned_data


class StudyTableEventForm(EventForm):
    class Meta(EventForm.Meta):
        model = StudyTableEvent


class ScholarshipEventForm(EventForm):
    class Meta(EventForm.Meta):
        model = ScholarshipEvent


class HealthAndSafetyEventForm(EventForm):
    class Meta(EventForm.Meta):
        model = HealthAndSafetyEvent


class ChapterEventForm(EventForm):
    class Meta(EventForm.Meta):
        model = ChapterEvent
        fields = EventForm.Meta.fields + ['minutes']


class RecruitmentEventForm(EventForm):
    class Meta(EventForm.Meta):
        model = RecruitmentEvent
        fields = ['name', 'mandatory', 'rush', 'date', 'start_time', 'end_time', 'picture', 'location', 'description']


class PhilanthropyEventForm(EventForm):
    class Meta(EventForm.Meta):
        model = PhilanthropyEvent


class ServiceEventForm(EventForm):
    class Meta(EventForm.Meta):
        model = ServiceEvent


class CommitteeMeetingForm(EventForm):
    class Meta(EventForm.Meta):
        model = CommitteeMeetingEvent


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
            'birthday': SelectDateWidget(years=YEAR_RANGE),
        }


class SuppliesForm(forms.ModelForm):
    class Meta:
        model = Supplies
        fields = ['what']


class MABEditCandidateForm(forms.Form):
    candidate = forms.ModelChoiceField(queryset=Brother.objects.filter(brother_status='0'), required=True)


class MeetABrotherEditForm(forms.Form):
    update = forms.BooleanField(label="", required=False)

    def __init__(self, *args, **kwargs):
        brother = Brother.objects.get(pk=kwargs.pop('brother', ""))
        exists = kwargs.pop('mab_exists', "")
        super(MeetABrotherEditForm, self).__init__(*args, **kwargs)

        #sets the label for each form as the brother the form relates to and sets the initial for the checkbox to whether or not the meet a brother exists
        if brother:
            self.fields['update'].label = brother.first_name + ' ' + brother.last_name
            self.fields['update'].initial = exists


class MeetABrotherForm(forms.Form):
    randomize = forms.BooleanField(label="", required=False)
    assigned_brother1 = forms.ModelChoiceField(queryset=Brother.objects.all(), required=False, empty_label="No Brother")
    assigned_brother2 = forms.ModelChoiceField(queryset=Brother.objects.all(), required=False, empty_label="No Brother")

    def __init__(self, *args, **kwargs):
        candidate = kwargs.pop('candidate', "")
        super(MeetABrotherForm, self).__init__(*args, **kwargs)

        if candidate:
            self.fields['randomize'].label = candidate


class EditBrotherAttendanceForm(forms.Form):
    """Form for adding or removing brothers from an event's eligible_attendees list
        Accepts event_id to get the current list of eligible_attendees
    
    """
    brothers_list = Brother.objects.exclude(brother_status='2').order_by('user__last_name', 'user__first_name')
    # the default for the queryset is all non-alumni
    add_brothers = forms.ModelMultipleChoiceField(
        queryset=brothers_list,
        widget=forms.SelectMultiple,
        label="Add Brothers",
        required=False,
    )

    remove_brothers = forms.ModelMultipleChoiceField(
        queryset=brothers_list,
        widget=forms.SelectMultiple,
        label="Remove Brothers",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        # gets the id of the event passed in when the form is initialized
        event_id = kwargs.pop('event', "")
        super(EditBrotherAttendanceForm, self).__init__(*args, **kwargs)

        # if an event was passed in, sets queryset for add_brothers to non-alumni not in the event's eligible_attendees
        # and queryset for remove_brothers to non-alumni that are in the event's eligible_attendees
        if event_id:
            brothers_list = Brother.objects.exclude(brother_status='2').order_by('user__last_name', 'user__first_name')
            eligible_attendees = Event.objects.get(pk=event_id).eligible_attendees.values('pk')
            self.fields['add_brothers'].queryset = brothers_list.exclude(id__in=eligible_attendees)
            self.fields['remove_brothers'].queryset = brothers_list.filter(id__in=eligible_attendees)


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
    brothers = Brother.objects.filter(
        brother_status='1'
    ).order_by('user__last_name', 'user__first_name')

    in_house = forms.ModelMultipleChoiceField(
        queryset=brothers,
        widget=forms.CheckboxSelectMultiple(),
        label="",
        required=False,
        initial=brothers.filter(in_house=True),
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
