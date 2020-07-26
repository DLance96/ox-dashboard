import csv
import random

from django.contrib import messages, auth
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import *
from django.views.generic.edit import UpdateView, DeleteView
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from .utils import verify_position, get_semester, verify_brother,\
        get_season, get_year, forms_is_valid, get_season_from, ec, non_ec,\
        build_thursday_detail_email, build_sunday_detail_email, calc_fines
from datetime import datetime
from .forms import *


class LoginView(View):
    """ Logs in and redirects to the homepage """

    def post(self, request, *args, **kwargs):
        user = auth.authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is not None:
            if user.is_active:
                auth.login(request, user)
        return HttpResponseRedirect(reverse('dashboard:home'))

    def get(self, request, *args, **kwargs):
        # we should never get to this code path
        return HttpResponseRedirect(reverse('dashboard:home'))


class LogoutView(View):
    """ Logout and redirect to homepage """

    def get(self, request, *args, **kwargs):
        auth.logout(request)
        return HttpResponseRedirect(reverse('dashboard:home'))


def change_password(request):
    if not request.user.is_authenticated():  # brother auth check
        messages.error(request, "Cannot change password if you are not logged in")
        return HttpResponseRedirect(reverse('dashboard:home'))
    brother = Brother.objects.filter(user=request.user)[0]
    form = ChangePasswordForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.cleaned_data
            user = auth.authenticate(
                username=request.user.username,
                password=instance['old_password']
            )
            if user is not None:
                if instance['new_password'] == instance['retype_new_password']:
                    if instance['new_password'] == instance['old_password']:
                        messages.error(request, "Old password and new password cannot match")
                        return HttpResponseRedirect(reverse('dashboard:change_password'))
                    else:
                        user.set_password(instance['new_password'])
                        user.save()
                        user = auth.authenticate(
                            username=request.user.username,
                            password=instance['new_password']
                        )
                        auth.login(request, user)
                        return HttpResponseRedirect(reverse('dashboard:brother'))
                else:
                    messages.error(request, "New password did not match")
                    return HttpResponseRedirect(reverse('dashboard:change_password'))

    context = {
        'brother': brother,
        'form': form,
    }

    return render(request, "change-password.html", context)


def home(request):
    """ Renders home page """
    context = {
    }
    return render(request, 'home.html', context)


def brother_info_list(request):
    """ Renders brother info page """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name")

    context = {
        'brothers': brothers,
    }
    return render(request, 'brother-info-list.html', context)


@login_required
def contact_list(request):
    """ Renders contact info page """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name")

    context = {
        'brothers': brothers,
    }
    return render(request, 'contact-list.html', context)


@login_required
def emergency_contact_list(request):
    """ Renders emergency contact info page """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name")

    context = {
        'brothers': brothers,
    }
    return render(request, 'emergency-contact-list.html', context)


def event_list(request):
    """Renders all the semester events"""
    chapter_events = ChapterEvent.objects.filter(semester=get_semester()).order_by("date")
    recruitment_events = RecruitmentEvent.objects.filter(semester=get_semester()).order_by("date")
    service_events = ServiceEvent.objects.filter(semester=get_semester()).order_by("date")
    philanthropy_events = PhilanthropyEvent.objects.filter(semester=get_semester()).order_by("date")

    context = {
        'chapter_events': chapter_events,
        'recruitment_events': recruitment_events,
        'service_events': service_events,
        'philanthropy_events': philanthropy_events,
    }

    return render(request, "event-list.html", context)


def brother_view(request):
    """ Renders the brother page of current user showing all standard brother information """
    if not request.user.is_authenticated():  # brother auth check
        messages.error(request, "Brother needs to be logged in before viewing brother portal")
        return HttpResponseRedirect(reverse('dashboard:home'))
    brother = Brother.objects.filter(user=request.user)[0]
    hs_events = HealthAndSafteyEvent.objects.filter(semester=get_semester()).order_by("date")
    chapter_events = ChapterEvent.objects.filter(semester=get_semester()).order_by("date")

    excuses_pending = Excuse.objects.filter(brother=brother, event__semester=get_semester(),
                                            status='0').order_by("event__date")
    excuses_approved = Excuse.objects.filter(brother=brother, event__semester=get_semester(),
                                             status='1').order_by("event__date")
    excuses_denied = Excuse.objects.filter(brother=brother, event__semester=get_semester(),
                                           status='2').order_by("event__date")
    excuses_not_mandatory = Excuse.objects.filter(brother=brother, event__semester=get_semester(),
                                                  status='3').order_by("event__date")

    # Event attendance value
    attendance = []
    past_chapter_event_count = 0
    chapter_event_attendance = 0
    unexcused_events = 0
    for event in chapter_events:
        if int(event.date.strftime("%s")) > int(datetime.datetime.now().strftime("%s")):
            attendance.append('')
        elif not event.mandatory:
            attendance.append('Not Mandatory')
        else:
            past_chapter_event_count += 1
            if event.attendees_brothers.filter(id=brother.id):
                attendance.append('Attended')
                chapter_event_attendance += 1
            elif excuses_approved.filter(event=event):
                attendance.append('Excused')
                chapter_event_attendance += 1
            elif excuses_pending.filter(event=event):
                attendance.append('Pending')
            else:
                attendance.append('Unexcused')
                unexcused_events += 1

    event_attendance = zip(chapter_events, attendance)
    chapter_attendance = "%s / %s" % (chapter_event_attendance, past_chapter_event_count)

    committee_reverse = dict((v, k) for k, v in COMMITTEE_CHOICES)
    standing_meetings = []
    operational_meetings = []
    if brother.get_operational_committee_display() != 'Unassigned':
        operational_meetings = CommitteeMeetingEvent.objects.filter(semester=get_semester(),
                                                                    committee=committee_reverse[
                                                                        brother.get_operational_committee_display()]) \
            .order_by("start_time").order_by("date")
    if brother.get_standing_committee_display() != 'Unassigned':
        standing_meetings = CommitteeMeetingEvent.objects.filter(semester=get_semester(),
                                                                 committee=committee_reverse[
                                                                     brother.get_standing_committee_display()]) \
            .order_by("start_time").order_by("date")

    current_season = get_season()
    if current_season is '0':
        recruitment_events = RecruitmentEvent.objects.filter(semester__season='0', semester__year=get_year()) \
            .order_by("date")
        recruitment_events_next = RecruitmentEvent.objects.filter(semester__season='2', semester__year=get_year()) \
            .order_by("date")
    else:
        recruitment_events = RecruitmentEvent.objects.filter(semester__season='2', semester__year=get_year()) \
            .order_by("date")
        recruitment_events_next = RecruitmentEvent.objects.filter(semester__season='0', semester__year=get_year()) \
            .order_by("date")
    pnms = PotentialNewMember.objects.filter(Q(primary_contact=brother) |
                                             Q(secondary_contact=brother) |
                                             Q(tertiary_contact=brother)).order_by("last_name")
    service_events = ServiceEvent.objects.filter(semester=get_semester()).order_by("date")
    # Service submissions
    submissions_pending = ServiceSubmission.objects.filter(brother=brother, semester=get_semester(),
                                                           status='0').order_by("date")
    submissions_submitted = ServiceSubmission.objects.filter(brother=brother, semester=get_semester(),
                                                             status='1').order_by("date")
    submissions_approved = ServiceSubmission.objects.filter(brother=brother, semester=get_semester(),
                                                            status='2').order_by("date")
    submissions_denied = ServiceSubmission.objects.filter(brother=brother, semester=get_semester(),
                                                          status='3').order_by("date")

    hours_pending = 0
    for submission in submissions_pending:
        hours_pending += submission.hours
    for submission in submissions_submitted:
        hours_pending += submission.hours

    hours_approved = 0
    for submission in submissions_approved:
        hours_approved += submission.hours

    philanthropy_events = PhilanthropyEvent.objects.filter(semester=get_semester()) \
        .order_by("start_time").order_by("date")

    context = {
        'brother': brother,
        'event_attendance': event_attendance,
        'chapter_attendance': chapter_attendance,
        'unexcused_events': unexcused_events,
        'operational_meetings': operational_meetings,
        'standing_meetings': standing_meetings,
        'excuses_pending': excuses_pending,
        'excuses_approved': excuses_approved,
        'excuses_denied': excuses_denied,
        'excuses_not_mandatory': excuses_not_mandatory,
        'hs_events': hs_events,
        'recruitment_events': recruitment_events,
        'recruitment_events_next': recruitment_events_next,
        'pnms': pnms,
        'service_events': service_events,
        'submissions_pending': submissions_pending,
        'submissions_submitted': submissions_submitted,
        'submissions_approved': submissions_approved,
        'submissions_denied': submissions_denied,
        'philanthropy_events': philanthropy_events,
        'hours_approved': hours_approved,
        'hours_pending': hours_pending,
    }
    return render(request, "brother.html", context)


def brother_chapter_event(request, event_id):
    """ Renders the brother page for chapter event with a excuse form """
    if not request.user.is_authenticated():  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother chapter events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    event = ChapterEvent.objects.get(pk=event_id)
    form = ExcuseForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            if instance.description == "I will not be attending because":
                context = {
                    'type': 'brother-view',
                    'form': form,
                    'event': event,
                    'error_message': "Please write a description",
                }
                return render(request, "chapter-event.html", context)
            brother = Brother.objects.filter(user=request.user)[0]
            instance.brother = brother
            instance.event = event
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'type': 'brother-view',
        'form': form,
        'event': event,
    }
    return render(request, "chapter-event.html", context)


def brother_service_event(request, event_id):
    """ Renders the brother page for service event with a excuse form """
    if not request.user.is_authenticated():  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother chapter events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brother = Brother.objects.filter(user=request.user)[0]
    event = ServiceEvent.objects.get(pk=event_id)
    brothers_rsvp = event.rsvp_brothers.all()
    rsvp_brother = event.rsvp_brothers.filter(id=brother.id)

    if request.method == 'POST':
        if rsvp_brother.exists():
            event.rsvp_brothers.remove(brother)
        else:
            event.rsvp_brothers.add(brother)
        event.save()
        return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'type': 'brother-view',
        'brothers_rsvp': brothers_rsvp,
        'rsvpd': rsvp_brother.exists(),
        'event': event,
    }

    return render(request, "service-event.html", context)


def brother_philanthropy_event(request, event_id):
    """ Renders the brother page for service event with a excuse form """
    if not request.user.is_authenticated():  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother chapter events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brother = Brother.objects.filter(user=request.user)[0]
    event = PhilanthropyEvent.objects.get(pk=event_id)
    brothers_rsvp = event.rsvp_brothers.all()
    rsvp_brother = event.rsvp_brothers.filter(id=brother.id)

    if request.method == 'POST':
        if rsvp_brother.exists():
            event.rsvp_brothers.remove(brother)
        else:
            event.rsvp_brothers.add(brother)
        event.save()
        return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'type': 'brother-view',
        'brothers_rsvp': brothers_rsvp,
        'rsvpd': rsvp_brother.exists(),
        'event': event,
    }

    return render(request, "philanthropy-event.html", context)


def brother_recruitment_event(request, event_id):
    """ Renders the brother page for recruitment event with a excuse form """
    if not request.user.is_authenticated():  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother chapter events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    event = RecruitmentEvent.objects.get(pk=event_id)
    attendees_pnms = event.attendees_pnms.all()

    context = {
        'type': 'brother-view',
        'attendees_pnms': attendees_pnms,
        'event': event,
    }
    return render(request, "recruitment-event.html", context)


def brother_hs_event(request, event_id):
    """ Renders the brother page for health and safety event with a excuse form """
    if not request.user.is_authenticated():  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother Health and Safety events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    event = HealthAndSafteyEvent.objects.get(pk=event_id)

    context = {
        'type': 'brother-view',
        'event': event,
    }
    return render(request, "hs-event.html", context)


def brother_excuse(request, excuse_id):
    """ Renders the brother page for one of their excuses """
    excuse = Excuse.objects.get(pk=excuse_id)
    if not request.user == excuse.brother.user:  # brother auth check
        messages.error(request, "Please log into the brother that submitted that excuse")
        return HttpResponseRedirect(reverse('dashboard:home'))

    context = {
        'excuse': excuse,
        'type': 'review',
    }
    return render(request, "excuse.html", context)


class ExcuseDelete(DeleteView):
    def get(self, request, *args, **kwargs):
        excuse = Excuse.objects.get(pk=self.kwargs['pk'])
        brother = excuse.brother
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ExcuseDelete, self).get(request, *args, **kwargs)

    model = Excuse
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:brother')


class ExcuseEdit(UpdateView):
    def get(self, request, *args, **kwargs):
        excuse = Excuse.objects.get(pk=self.kwargs['pk'])
        brother = excuse.brother
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ExcuseEdit, self).get(request, *args, **kwargs)

    model = Excuse
    success_url = reverse_lazy('dashboard:brother')
    fields = ['description']


class BrotherEdit(UpdateView):
    def get(self, request, *args, **kwargs):
        brother = Brother.objects.get(pk=self.kwargs['pk'])
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(BrotherEdit, self).get(request, *args, **kwargs)

    model = Brother
    success_url = reverse_lazy('dashboard:brother')
    fields = ['first_name', 'last_name', 'roster_number', 'semester_joined', 'school_status', 'brother_status',
              'major', 'minor', 't_shirt_size', 'case_ID', 'birthday', 'hometown', 'phone_number',
              'emergency_contact_phone_number', 'emergency_contact', 'room_number',
              'address']


def brother_pnm(request, pnm_id):
    """ Renders the pnm page for brothers """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Please log in to view pnms")
        return HttpResponseRedirect(reverse('dashboard:home'))

    pnm = PotentialNewMember.objects.get(pk=pnm_id)
    events = RecruitmentEvent.objects.filter(semester=get_season()).order_by("date").all()

    attended_events = []
    for event in events:
        if event.attendees_pnms.filter(id=pnm_id).exists():
            attended_events.append(event)

    context = {
        'type': 'brother-view',
        'pnm': pnm,
        'events': attended_events,
    }
    return render(request, 'potential-new-member.html', context)


def brother_service_submission(request, submission_id):
    """ Renders the Brother page for viewing a service submission"""
    if not request.user.is_authenticated():  # brother auth check
        messages.error(request, "Brother not logged in before adding service hours")
        return HttpResponseRedirect(reverse('dashboard:home'))

    submission = ServiceSubmission.objects.get(pk=submission_id)

    context = {
        'type': 'review',
        'submission': submission,
    }

    return render(request, 'service-submission.html', context)


def brother_service_submission_add(request):
    """ Renders the Brother page for adding a service submission"""
    if not request.user.is_authenticated():  # brother auth check
        messages.error(request, "Brother not logged in before adding service hours")
        return HttpResponseRedirect(reverse('dashboard:home'))

    form = ServiceSubmissionForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            semester = get_semester()
            brother = Brother.objects.filter(user=request.user)[0]
            instance.brother = brother
            instance.semester = semester
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'title': 'Submit Service Hours',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class ServiceSubmissionDelete(DeleteView):
    def get(self, request, *args, **kwargs):
        submission = ServiceSubmission.objects.get(pk=self.kwargs['pk'])
        brother = submission.brother
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ServiceSubmissionDelete, self).get(request, *args, **kwargs)

    template_name = 'dashboard/base_confirm_delete.html'
    model = ServiceSubmission
    success_url = reverse_lazy('dashboard:brother')


class ServiceSubmissionEdit(UpdateView):
    def get(self, request, *args, **kwargs):
        submission = ServiceSubmission.objects.get(pk=self.kwargs['pk'])
        brother = submission.brother
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ServiceSubmissionEdit, self).get(request, *args, **kwargs)

    model = ServiceSubmission
    success_url = reverse_lazy('dashboard:brother')
    fields = ['name', 'date', 'description', 'hours', 'status']


@verify_position(['President', 'Adviser'])
def president(request):
    """ Renders the President page and all relevant information """
    return render(request, 'president.html', {})


@verify_position(['Vice President', 'President', 'Adviser'])
def vice_president(request):
    """ Renders the Vice President page and all relevant information, primarily committee related """
    committee_meetings = CommitteeMeetingEvent.objects.filter(semester=get_semester())\
        .order_by("start_time").order_by("date")

    context = {
        'committee_meetings': committee_meetings,
    }

    return render(request, 'vice-president.html', context)


@verify_position(['Vice President', 'President', 'Adviser'])
def vice_president_committee_assignments(request):
    """Renders Committee assignment update page for the Vice President"""
    form_list = []
    brothers = Brother.objects.exclude(brother_status='2')
    for brother in brothers:
        new_form = CommitteeForm(request.POST or None, initial={'standing_committee': brother.standing_committee,
                                                                'operational_committee': brother.operational_committee},
                                 prefix=brother.id)
        form_list.append(new_form)

    brother_forms = zip(brothers, form_list)

    if request.method == 'POST':
        if forms_is_valid(form_list):
            for counter, form in enumerate(form_list):
                instance = form.cleaned_data
                brother = brothers[counter]
                brother.standing_committee = instance['standing_committee']
                brother.operational_committee = instance['operational_committee']
                brother.save()
            return HttpResponseRedirect(reverse('dashboard:vice_president'))

    context = {
        'brother_forms': brother_forms,
    }

    return render(request, 'committee-assignment.html', context)


@verify_position(['Vice President', 'President', 'Adviser'])
def vice_president_committee_meeting_add(request):
    """ Renders the committee meeting add page """
    form = CommitteeMeetingForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)

            try:
                semester = Semester.objects.filter(season=get_season_from(instance.date.month),
                                                   year=instance.date.year)[0]
            except IndexError:
                semester = Semester(season=get_season_from(instance.date.month),
                                    year=instance.date.year)
                semester.save()

            instance.semester = semester
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:vice_president'))

    context = {
        'title': 'Committee Meeting',
        'form': form,
    }
    return render(request, 'event-add.html', context)


class CommitteeMeetingDelete(DeleteView):
    @verify_position(['Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(CommitteeMeetingDelete, self).get(request, *args, **kwargs)

    model = CommitteeMeetingEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:vice_president')


class CommitteeMeetingEdit(UpdateView):
    @verify_position(['Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(CommitteeMeetingEdit, self).get(request, *args, **kwargs)

    model = CommitteeMeetingEvent
    success_url = reverse_lazy('dashboard:vice_president')
    fields = ['date', 'start_time', 'semester', 'committee', 'minutes']


@verify_position(['President', 'Adviser', 'Vice President', 'Vice President of Health and Safety'])
def vphs(request):
    """ Renders the VPHS and the events they can create """
    events = HealthAndSafteyEvent.objects.filter(semester=get_semester()).order_by("start_time").order_by("date")

    context = {
        'events': events,
    }
    return render(request, 'vphs.html', context)


@verify_position(['President', 'Adviser', 'Vice President', 'Vice President of Health and Safety'])
def health_and_saftey_event_add(request):
    """ Renders the VPHS adding an event """
    form = HealthAndSafetyEventForm(request.POST or None)

    if form.is_valid():
        # TODO: add google calendar event adding
        instance = form.save(commit=False)
        try:
            semester = Semester.objects.filter(season=get_season_from(instance.date.month),
                                               year=instance.date.year)[0]
        except IndexError:
            semester = Semester(season=get_season_from(instance.date.month),
                                year=instance.date.year)
            semester.save()
        if instance.end_time is not None and instance.end_time < instance.start_time:
            context = {
                'position': 'Vice President of Health and Safety',
                'form': form,
                'error_message': "Start time after end time!",
            }
            return render(request, "event-add.html", context)
        instance.semester = semester
        instance.save()
        return HttpResponseRedirect(reverse('dashboard:vphs'))

    context = {
        'title': 'Add New Health and Safety Event',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class HealthAndSafteyEdit(UpdateView):
    @verify_position(['President', 'Adviser', 'Vice President', 'Vice President of Health and Safety'])
    def get(self, request, *args, **kwargs):
        return super(HealthAndSafteyEdit, self).get(request, *args, **kwargs)

    model = HealthAndSafteyEvent
    success_url = reverse_lazy('dashboard:vphs')
    fields = ['name', 'date', 'start_time', 'end_time', 'notes', 'minutes']


class HealthAndSafteyDelete(DeleteView):
    @verify_position(['President', 'Adviser', 'Vice President', 'Vice President of Health and Safety'])
    def get(self, request, *args, **kwargs):
        return super(HealthAndSafteyDelete, self).get(request, *args, **kwargs)

    model = HealthAndSafteyEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:vphs')


def health_and_saftey_event(request, event_id):
    """ Renders the vphs way of view events """
    event = HealthAndSafteyEvent.objects.get(pk=event_id)
    brothers = Brother.objects.exclude(brother_status='2')
    brother_form_list = []

    for brother in brothers:
        if event.attendees_brothers.filter(id=brother.id):
            new_form = BrotherAttendanceForm(request.POST or None, initial={'present': True},
                                             prefix=brother.roster_number,
                                             brother="- %s %s" % (brother.first_name, brother.last_name))
            brother_form_list.append(new_form)
        else:
            new_form = BrotherAttendanceForm(request.POST or None, initial={'present': False},
                                             prefix=brother.roster_number,
                                             brother="- %s %s" % (brother.first_name, brother.last_name))
            brother_form_list.append(new_form)

    if request.method == 'POST':
        if forms_is_valid(brother_form_list):
            for counter, form in enumerate(brother_form_list):
                instance = form.cleaned_data
                if instance['present'] is True:
                    event.attendees_brothers.add(brothers[counter])
                    event.save()
                if instance['present'] is False:
                    event.attendees_brothers.remove(brothers[counter])
                    event.save()
            return HttpResponseRedirect(reverse('dashboard:scholarship_c'))

    context = {
        'type': 'attendance',
        'brother_form_list': brother_form_list,
        'event': event,
    }
    return render(request, "hs-event.html", context)


@verify_position(['Treasurer', 'President', 'Adviser'])
def treasurer(request):
    """ Renders all the transactional information on the site for the treasurer """
    return render(request, 'treasurer.html', {})


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary(request):
    """ Renders the secretary page giving access to excuses and ChapterEvents """
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='0').order_by("event__date")
    events = ChapterEvent.objects.filter(semester=get_semester()).order_by("start_time").order_by("date")

    context = {
        'excuses': excuses,
        'events': events,
    }
    return render(request, 'secretary.html', context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_attendance(request):
    """ Renders the secretary view for chapter attendance """
    brothers = Brother.objects.exclude(brother_status='2').order_by('last_name')
    events = ChapterEvent.objects.filter(semester=get_semester(), mandatory=True)\
        .exclude(date__gt=datetime.date.today())
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='1')
    events_excused_list = []
    events_unexcused_list = []

    for brother in brothers:
        events_excused = 0
        events_unexcused = 0
        for event in events:
            if not event.attendees_brothers.filter(id=brother.id).exists():
                if excuses.filter(brother=brother, event=event).exists():
                    events_excused += 1
                else:
                    events_unexcused += 1
        events_excused_list.append(events_excused)
        events_unexcused_list.append(events_unexcused)

    brother_attendance = zip(brothers, events_excused_list, events_unexcused_list)

    context = {
        'brother_attendance': brother_attendance,
    }

    return render(request, 'chapter-event-attendance.html', context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_event(request, event_id):
    """ Renders the attendance sheet for any event """
    event = ChapterEvent.objects.get(pk=event_id)
    brothers = Brother.objects.exclude(brother_status='2').order_by('last_name')
    form_list = []
    for brother in brothers:
        if event.attendees_brothers.filter(id=brother.id):
            new_form = BrotherAttendanceForm(request.POST or None, initial={'present': True},
                                             prefix=brother.roster_number,
                                             brother="- %s %s" % (brother.first_name, brother.last_name))
            form_list.append(new_form)
        else:
            new_form = BrotherAttendanceForm(request.POST or None, initial={'present': False},
                                             prefix=brother.roster_number,
                                             brother="- %s %s" % (brother.first_name, brother.last_name))
            form_list.append(new_form)

    if request.method == 'POST':
        if forms_is_valid(form_list):
            for counter, form in enumerate(form_list):
                instance = form.cleaned_data
                if instance['present'] is True:
                    event.attendees_brothers.add(brothers[counter])
                    event.save()
                if instance['present'] is False:
                    event.attendees_brothers.remove(brothers[counter])
                    event.save()
            return HttpResponseRedirect(reverse('dashboard:secretary'))

    context = {
        'type': 'attendance',
        'brother_form_list': form_list,
        'event': event,
    }
    return render(request, "chapter-event.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_excuse(request, excuse_id):
    """ Renders Excuse response form """
    excuse = get_object_or_404(Excuse, pk=excuse_id)
    form = ExcuseResponseForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            if instance.status == '2' and instance.response_message == '':
                context = {
                    'type': 'response',
                    'excuse': excuse,
                    'form': form,
                    'error_message': "Response message required for denial"
                }
                return render(request, "excuse.html", context)
            if instance.status == '3' and excuse.event.mandatory:
                context = {
                    'type': 'response',
                    'excuse': excuse,
                    'form': form,
                    'error_message': "Event is mandatory cannot mark excuse not mandatory"
                }
                return render(request, "excuse.html", context)
            else:
                excuse.status = instance.status
                excuse.response_message = instance.response_message
                excuse.save()
                return HttpResponseRedirect(reverse('dashboard:secretary'))

    context = {
        'type': 'response',
        'excuse': excuse,
        'form': form,
    }
    return render(request, "excuse.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_all_excuses(request):
    """ Renders Excuse """
    excuses = Excuse.objects.order_by('brother__last_name','event__date')

    context = {
        'excuses': excuses
    }
    return render(request, 'secretary_excuses.html', context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_event_view(request, event_id):
    """ Renders the Secretary way of viewing old events """
    event = ChapterEvent.objects.get(pk=event_id)
    attendees = event.attendees_brothers.all().order_by("last_name")

    context = {
        'type': 'ec-view',
        'attendees': attendees,
        'event': event,
    }
    return render(request, "chapter-event.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_brother_list(request):
    """ Renders the Secretary way of viewing brothers """
    brothers = Brother.objects.exclude(brother_status='2')
    context = {
        'position': 'Secretary',
        'brothers': brothers
    }
    return render(request, "brother-list.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_brother_view(request, brother_id):
    """ Renders the Secretary way of viewing a brother """
    brother = Brother.objects.get(pk=brother_id)
    context = {
        'brother': brother
    }
    return render(request, "brother-view.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_brother_add(request):
    """ Renders the Secretary way of viewing a brother """
    form = BrotherForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.cleaned_data
            if instance['password'] == instance['password2']:
                user = User.objects.create_user(instance['case_ID'], instance['case_ID'] + "@case.edu",
                                                instance['password'])
                user.last_name = instance['last_name']
                user.save()

                brother = form.save(commit=False)
                brother.user = user
                brother.save()

                return HttpResponseRedirect(reverse('dashboard:secretary_brother_list'))
            else:
                context = {
                    'error_message': "Please make sure your passwords match",
                    'title': 'Add New Brother',
                    'form': form,
                }
                return render(request, 'model-add.html', context)

    context = {
        'title': 'Add New Brother',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class SecretaryBrotherEdit(UpdateView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(SecretaryBrotherEdit, self).get(request, *args, **kwargs)

    model = Brother
    success_url = reverse_lazy('dashboard:secretary_brother_list')
    fields = ['first_name', 'last_name', 'roster_number', 'semester_joined', 'school_status', 'brother_status',
              'major', 'minor', 't_shirt_size', 'case_ID', 'birthday', 'hometown', 'phone_number',
              'emergency_contact_phone_number', 'emergency_contact', 'standing_committee', 'operational_committee',
              'room_number', 'address']


class SecretaryBrotherDelete(DeleteView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(SecretaryBrotherDelete, self).get(request, *args, **kwargs)

    model = Brother
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:secretary')


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_event_add(request):
    """ Renders the Secretary way of adding ChapterEvents """
    form = ChapterEventForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            try:
                semester = Semester.objects.filter(season=get_season_from(instance.date.month),
                                                   year=instance.date.year)[0]
            except IndexError:
                semester = Semester(season=get_season_from(instance.date.month),
                                    year=instance.date.year)
                semester.save()
            if instance.end_time is not None and instance.end_time < instance.start_time:
                context = {
                    'position': 'Secretary',
                    'form': form,
                    'error_message': "Start time after end time!",
                }
                return render(request, "event-add.html", context)
            instance.semester = semester
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:secretary'))

    context = {
        'position': 'Secretary',
        'form': form,
    }
    return render(request, "event-add.html", context)


class ChapterEventEdit(UpdateView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ChapterEventEdit, self).get(request, *args, **kwargs)

    model = ChapterEvent
    success_url = reverse_lazy('dashboard:secretary')
    fields = ['name', 'mandatory', 'date', 'start_time', 'end_time', 'minutes', 'notes']


class ChapterEventDelete(DeleteView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ChapterEventDelete, self).get(request, *args, **kwargs)

    model = ChapterEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:secretary')


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_all_events(request):
    """ Renders a secretary view with all the ChapterEvent models ordered by date grouped by semester """
    events_by_semester = []
    semesters = Semester.objects.order_by("season").order_by("year").all()
    for semester in semesters:
        events = ChapterEvent.objects.filter(semester=semester).order_by("date")
        if len(events) == 0:
            events_by_semester.append([])
        else:
            events_by_semester.append(events)
    zip_list = zip(events_by_semester, semesters)
    context = {
        'list': zip_list,
        'position': "Secretary"
    }
    return render(request, "chapter-event-all.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_positions(request):
    """ Renders all of the positions currently in the chapter """
    # Checking to make sure all of the EC and dashboard required positions are setup
    for position in ec:
        if not Position.objects.filter(title=position).exists():
            new_position = Position(title=position, ec=True)
            new_position.save()
    for position in non_ec:
        if not Position.objects.filter(title=position).exists():
            new_position = Position(title=position)
            new_position.save()

    ec_positions = Position.objects.filter(ec=True)
    positions = Position.objects.filter(ec=False).order_by("title")

    context = {
        'positions': positions,
        'ec_positions': ec_positions,
    }
    return render(request, "positions.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_position_add(request):
    """ Renders the Secretary way of viewing a brother """
    form = PositionForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('dashboard:secretary_positions'))

    context = {
        'title': 'Add New Position',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class PositionEdit(UpdateView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PositionEdit, self).get(request, *args, **kwargs)

    model = Position
    success_url = reverse_lazy('dashboard:secretary_positions')
    fields = ['brother']


class PositionDelete(DeleteView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PositionDelete, self).get(request, *args, **kwargs)

    model = Position
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:secretary_positions')


@verify_position(['Marshal', 'Vice President', 'President', 'Adviser'])
def marshal(request):
    """ Renders the marshal page listing all the candidates and relevant information to them """
    candidates = Brother.objects.filter(brother_status='0').order_by("last_name")
    events = ChapterEvent.objects.filter(semester=get_semester()).exclude(date__gt=datetime.date.today())
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='1')
    events_excused_list = []
    events_unexcused_list = []

    for candidate in candidates:
        events_excused = 0
        events_unexcused = 0
        if candidate.date_pledged:
            expected_events = events.exclude(date_pledged__lt=datetime.date.today())
        else:
            expected_events = events
        for event in expected_events:
            if not event.attendees_brothers.filter(id=candidate.id).exists():
                if excuses.filter(brother=candidate, event=event).exists():
                    events_excused += 1
                else:
                    events_unexcused += 1
        events_excused_list.append(events_excused)
        events_unexcused_list.append(events_unexcused)

    candidate_attendance = zip(candidates, events_excused_list, events_unexcused_list)

    context = {
        'candidates': candidates,
        'candidate_attendance': candidate_attendance,
    }
    return render(request, 'marshal.html', context)


@verify_position(['Marshal', 'Vice President', 'President', 'Adviser'])
def marshal_candidate(request, brother_id):
    """ Renders the marshal page to view candidate info """
    brother = Brother.objects.get(pk=brother_id)
    context = {
        'brother': brother
    }
    return render(request, "brother-view.html", context)


@verify_position(['Marshal', 'Vice President', 'President', 'Adviser'])
def marshal_candidate_add(request):
    """ Renders the Marshal way of viewing a candidate """
    form = BrotherForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.cleaned_data
            if instance['password'] == instance['password2']:
                user = User.objects.create_user(instance['case_ID'], instance['case_ID'] + "@case.edu",
                                                instance['password'])
                user.last_name = instance['last_name']
                user.save()

                brother = form.save(commit=False)
                brother.user = user
                brother.save()

                return HttpResponseRedirect(reverse('dashboard:marshal'))
            else:
                context = {
                    'error_message': "Please make sure your passwords match",
                    'title': 'Add New Candidate',
                    'form': form,
                }
                return render(request, 'model-add.html', context)

    context = {
        'title': 'Add New Candidate',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class CandidateEdit(UpdateView):
    @verify_position(['Marshal', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(CandidateEdit, self).get(request, *args, **kwargs)

    model = Brother
    success_url = reverse_lazy('dashboard:marshal')
    fields = [
        'first_name', 'last_name', 'roster_number', 'semester_joined',
        'school_status', 'brother_status', 'major', 'minor', 't_shirt_size',
        'case_ID', 'birthday', 'hometown', 'phone_number',
        'emergency_contact_phone_number', 'emergency_contact', 'room_number',
        'address'
    ]


class CandidateDelete(DeleteView):
    @verify_position(['Marshal', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(CandidateDelete, self).get(request, *args, **kwargs)

    model = Brother
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:marshal')


@verify_position(['Scholarship Chair', 'President', 'Adviser'])
def scholarship_c(request):
    """ Renders the Scholarship page listing all brother gpas and study table attendance """
    events = StudyTableEvent.objects.filter(semester=get_semester()).order_by("date")

    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name")
    plans = []

    for brother in brothers:
        plan = ScholarshipReport.objects.filter(semester=get_semester(), brother__id=brother.id)
        if plan.exists():
            plan = plan[0]
        else:
            plan = ScholarshipReport(brother=brother, semester=get_semester())
            plan.save()
        plans.append(plan)

    brother_plans = zip(brothers, plans)

    context = {
        'events': events,
        'brother_plans': brother_plans,
    }
    return render(request, "scholarship-chair.html", context)


@verify_position(['Scholarship Chair', 'President', 'Adviser'])
def study_table_event(request, event_id):
    """ Renders the scholarship chair way of view StudyTables """
    event = StudyTableEvent.objects.get(pk=event_id)
    brothers = Brother.objects.exclude(brother_status='2')
    brother_form_list = []

    for brother in brothers:
        if event.attendees_brothers.filter(id=brother.id):
            new_form = BrotherAttendanceForm(request.POST or None, initial={'present': True},
                                             prefix=brother.roster_number,
                                             brother="- %s %s" % (brother.first_name, brother.last_name))
            brother_form_list.append(new_form)
        else:
            new_form = BrotherAttendanceForm(request.POST or None, initial={'present': False},
                                             prefix=brother.roster_number,
                                             brother="- %s %s" % (brother.first_name, brother.last_name))
            brother_form_list.append(new_form)

    if request.method == 'POST':
        if forms_is_valid(brother_form_list):
            for counter, form in enumerate(brother_form_list):
                instance = form.cleaned_data
                if instance['present'] is True:
                    event.attendees_brothers.add(brothers[counter])
                    event.save()
                if instance['present'] is False:
                    event.attendees_brothers.remove(brothers[counter])
                    event.save()
            return HttpResponseRedirect(reverse('dashboard:scholarship_c'))

    context = {
        'type': 'attendance',
        'brother_form_list': brother_form_list,
        'event': event,
    }
    return render(request, "studytable-event.html", context)


@verify_position(['Scholarship Chair', 'President', 'Adviser'])
def scholarship_c_event_add(request):
    """ Renders the scholarship chair way of adding StudyTableEvents """
    form = StudyTableEventForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            try:
                semester = Semester.objects.filter(season=get_season_from(instance.date.month),
                                                   year=instance.date.year)[0]
            except IndexError:
                semester = Semester(season=get_season_from(instance.date.month),
                                    year=instance.date.year)
                semester.save()
            if instance.end_time is not None and instance.end_time < instance.start_time:
                context = {
                    'position': 'Scholarship Chair',
                    'form': form,
                    'error_message': "Start time after end time!",
                }
                return render(request, "event-add.html", context)
            instance.semester = semester
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:scholarship_c'))

    context = {
        'position': 'Scholarship Chair',
        'form': form,
    }
    return render(request, "event-add.html", context)


class StudyEventDelete(DeleteView):
    @verify_position(['Scholarship Chair', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(StudyEventDelete, self).get(request, *args, **kwargs)

    model = StudyTableEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:scholarship_c')


class StudyEventEdit(UpdateView):
    @verify_position(['Scholarship Chair', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(StudyEventEdit, self).get(request, *args, **kwargs)

    model = StudyTableEvent
    success_url = reverse_lazy('dashboard:scholarship_c')
    fields = ['date', 'start_time', 'end_time', 'notes']


@verify_position(['Scholarship Chair', 'President', 'Adviser'])
def scholarship_c_plan(request, plan_id):
    """Renders Scholarship Plan page for the Scholarship Chair"""
    plan = ScholarshipReport.objects.get(pk=plan_id)
    events = StudyTableEvent.objects.filter(semester=get_semester()).exclude(date__gt=datetime.date.today())
    study_tables_attended = 0
    study_tables_count = len(events)

    for event in events:
        if event.attendees_brothers.filter(id=plan.brother.id).exists():
            study_tables_attended += 1

    context = {
        'type': 'scholarship-chair',
        'plan': plan,
        'study_tables_count': study_tables_count,
        'study_tables_attended': study_tables_attended,
    }

    return render(request, 'scholarship-report.html', context)


@verify_position(['Scholarship Chair', 'President', 'Adviser'])
def scholarship_c_gpa(request):
    """Renders Scholarship Gpa update page for the Scholarship Chair"""
    plans = ScholarshipReport.objects.filter(semester=get_semester()).order_by("brother__last_name")
    form_list = []

    for plan in plans:
        new_form = GPAForm(request.POST or None, initial={'cum_GPA': plan.cumulative_gpa,
                                                          'past_GPA': plan.past_semester_gpa}, prefix=plan.id)
        form_list.append(new_form)

    form_plans = zip(form_list, plans)

    if request.method == 'POST':
        if forms_is_valid(form_list):
            for counter, form in enumerate(form_list):
                instance = form.cleaned_data
                plan = plans[counter]
                plan.cumulative_gpa = instance['cum_GPA']
                plan.past_semester_gpa = instance['past_GPA']
                plan.save()
            return HttpResponseRedirect(reverse('dashboard:scholarship_c'))

    context = {
        'form_plans': form_plans,
    }

    return render(request, 'scholarship-gpa.html', context)


class ScholarshipReportEdit(UpdateView):
    @verify_position(['Scholarship Chair', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ScholarshipReportEdit, self).get(request, *args, **kwargs)

    model = ScholarshipReport
    success_url = reverse_lazy('dashboard:scholarship_c')
    fields = ['cumulative_gpa', 'past_semester_gpa', 'scholarship_plan', 'active']


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c(request):
    """ Renders Scholarship chair page with events for the current and following semester """
    current_season = get_season()
    if current_season is '0':
        semester_events = RecruitmentEvent.objects.filter(semester__season='0', semester__year=get_year())
        semester_events_next = RecruitmentEvent.objects.filter(semester__season='2', semester__year=get_year())
    else:
        semester_events = RecruitmentEvent.objects.filter(semester__season='2', semester__year=get_year())
        semester_events_next = RecruitmentEvent.objects.filter(semester__season='0', semester__year=get_year())

    potential_new_members = PotentialNewMember.objects.all()

    context = {
        'events': semester_events,
        'events_future': semester_events_next,
        'potential_new_members': potential_new_members,
    }
    return render(request, 'recruitment-chair.html', context)


def all_pnm_csv(request):
    """Returns a list of pnms as a csv"""
    potential_new_members = PotentialNewMember.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_pnms.csv"'
    writer = csv.writer(response)
    fields = [f.name for f in PotentialNewMember._meta.get_fields()][1:]
    writer.writerow(fields)
    for pnm in potential_new_members:
        row = []
        for field in fields:
            row.append(getattr(pnm, field))
        writer.writerow(row)

    return response


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_rush_attendance(request):
    """ Renders Scholarship chair page with rush attendance """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name")
    events = RecruitmentEvent.objects.filter(semester=get_semester(), rush=True) \
        .exclude(date__gt=datetime.date.today())
    events_attended_list = []

    for brother in brothers:
        events_attended = 0
        for event in events:
            if event.attendees_brothers.filter(id=brother.id).exists():
                events_attended += 1
        events_attended_list.append(events_attended)

    rush_attendance = zip(brothers, events_attended_list)

    context = {
        'rush_attendance': rush_attendance,
    }

    return render(request, 'rush_attendance.html', context)


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_pnm(request, pnm_id):
    """ Renders PNM view for recruitment chair """
    pnm = PotentialNewMember.objects.get(pk=pnm_id)
    events = RecruitmentEvent.objects.filter(semester=get_semester()).order_by("date").all()

    attended_events = []
    for event in events:
        if event.attendees_pnms.filter(id=pnm_id).exists():
            attended_events.append(event)

    context = {
        'type': 'recruitment-chair-view',
        'events': attended_events,
        'pnm': pnm,
    }
    return render(request, 'potential-new-member.html', context)


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_pnm_add(request):
    """ Renders the recruitment chair way of adding PNMs """
    form = PotentialNewMemberForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('dashboard:recruitment_c'))

    context = {
        'title': 'Add Potential New Member',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class PnmDelete(DeleteView):
    @verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PnmDelete, self).get(request, *args, **kwargs)

    model = PotentialNewMember
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:recruitment_c')


class PnmEdit(UpdateView):
    @verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PnmEdit, self).get(request, *args, **kwargs)

    model = PotentialNewMember
    success_url = reverse_lazy('dashboard:recruitment_c')
    fields = ['first_name', 'last_name', 'case_ID', 'phone_number', 'primary_contact', 'secondary_contact',
              'tertiary_contact', 'notes']


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_event(request, event_id):
    """ Renders the recruitment chair way of view RecruitmentEvents """
    event = RecruitmentEvent.objects.get(pk=event_id)
    pnms = PotentialNewMember.objects.all()
    brothers = Brother.objects.exclude(brother_status='2')
    pnm_form_list = []
    brother_form_list = []
    for pnm in pnms:
        if event.attendees_pnms.filter(pk=pnm.id):
            new_form = PnmAttendanceForm(request.POST or None, initial={'present': True}, prefix=pnm.id,
                                         pnm="- %s %s" % (pnm.first_name, pnm.last_name))
            pnm_form_list.append(new_form)
        else:
            new_form = PnmAttendanceForm(request.POST or None, initial={'present': False}, prefix=pnm.id,
                                         pnm="- %s %s" % (pnm.first_name, pnm.last_name))
            pnm_form_list.append(new_form)

    for brother in brothers:
        if event.attendees_brothers.filter(id=brother.id):
            new_form = BrotherAttendanceForm(request.POST or None, initial={'present': True},
                                             prefix=brother.roster_number,
                                             brother="- %s %s" % (brother.first_name, brother.last_name))
            brother_form_list.append(new_form)
        else:
            new_form = BrotherAttendanceForm(request.POST or None, initial={'present': False},
                                             prefix=brother.roster_number,
                                             brother="- %s %s" % (brother.first_name, brother.last_name))
            brother_form_list.append(new_form)

    if request.method == 'POST':
        if forms_is_valid(pnm_form_list) and forms_is_valid(brother_form_list):
            for counter, form in enumerate(pnm_form_list):
                instance = form.cleaned_data
                if instance['present'] is True:
                    event.attendees_pnms.add(pnms[counter])
                    event.save()
                if instance['present'] is False:
                    event.attendees_pnms.remove(pnms[counter])
                    event.save()
            for counter, form in enumerate(brother_form_list):
                instance = form.cleaned_data
                if instance['present'] is True:
                    event.attendees_brothers.add(brothers[counter])
                    event.save()
                if instance['present'] is False:
                    event.attendees_brothers.remove(brothers[counter])
                    event.save()
            return HttpResponseRedirect(reverse('dashboard:recruitment_c'))

    context = {
        'type': 'attendance',
        'pnm_form_list': pnm_form_list,
        'brother_form_list': brother_form_list,
        'event': event,
    }
    return render(request, "recruitment-event.html", context)


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_event_add(request):
    """ Renders the recruitment chair way of adding RecruitmentEvents """
    form = RecruitmentEventForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            try:
                semester = Semester.objects.filter(season=get_season_from(instance.date.month),
                                                   year=instance.date.year)[0]
            except IndexError:
                semester = Semester(season=get_season_from(instance.date.month),
                                    year=instance.date.year)
                semester.save()
            if instance.end_time is not None and instance.end_time < instance.start_time:
                context = {
                    'position': 'Recruitment Chair',
                    'form': form,
                    'error_message': "Start time after end time!",
                }
                return render(request, "event-add.html", context)
            instance.semester = semester
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:recruitment_c'))

    context = {
        'position': 'Recruitment Chair',
        'form': form,
    }
    return render(request, "event-add.html", context)


class RecruitmentEventDelete(DeleteView):
    @verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(RecruitmentEventDelete, self).get(request, *args, **kwargs)

    model = RecruitmentEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:recruitment_c')


class RecruitmentEventEdit(UpdateView):
    @verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(RecruitmentEventEdit, self).get(request, *args, **kwargs)

    model = RecruitmentEvent
    success_url = reverse_lazy('dashboard:recruitment_c')
    fields = ['name', 'rush', 'date', 'start_time', 'end_time', 'notes']


@verify_position(['Service Chair', 'ec'])
def service_c(request):
    """ Renders the service chair page with service submissions """
    events = ServiceEvent.objects.filter(semester=get_semester())
    submissions_pending = ServiceSubmission.objects.filter(semester=get_semester(), status='0').order_by("date")

    submissions_submitted = ServiceSubmission.objects.filter(semester=get_semester(), status='1').order_by(
        "date")

    hours_pending = 0
    for submission in submissions_pending:
        hours_pending += submission.hours
    for submission in submissions_submitted:
        hours_pending += submission.hours

    hours_approved = 0
    submissions_approved = ServiceSubmission.objects.filter(semester=get_semester(), status='2')
    for submission in submissions_approved:
        hours_approved += submission.hours

    context = {
        'events': events,
        'hours_approved': hours_approved,
        'hours_pending': hours_pending,
        'submissions_pending': submissions_pending,
        'submissions_submitted': submissions_submitted,
    }
    return render(request, 'service-chair.html', context)


@verify_position(['Service Chair', 'ec'])
def service_c_event(request, event_id):
    """ Renders the service chair way of adding ServiceEvent """
    event = ServiceEvent.objects.get(pk=event_id)
    brothers = Brother.objects.exclude(brother_status='2')
    brothers_rsvp = event.rsvp_brothers.all()
    form_list = []

    for brother in brothers:
        if event.attendees_brothers.filter(id=brother.id):
            new_form = BrotherAttendanceForm(request.POST or None, initial={'present': True},
                                             prefix=brother.roster_number,
                                             brother="- %s %s" % (brother.first_name, brother.last_name))
            form_list.append(new_form)
        else:
            new_form = BrotherAttendanceForm(request.POST or None, initial={'present': False},
                                             prefix=brother.roster_number,
                                             brother="- %s %s" % (brother.first_name, brother.last_name))
            form_list.append(new_form)

    if request.method == 'POST':
        if forms_is_valid(form_list):
            for counter, form in enumerate(form_list):
                instance = form.cleaned_data
                if instance['present'] is True:
                    event.attendees_brothers.add(brothers[counter])
                    event.save()
                if instance['present'] is False:
                    event.attendees_brothers.remove(brothers[counter])
                    event.save()
            return HttpResponseRedirect(reverse('dashboard:service_c'))

    context = {
        'type': 'attendance',
        'brother_form_list': form_list,
        'brothers_rsvp': brothers_rsvp,
        'event': event,
    }

    return render(request, 'service-event.html', context)


class ServiceEventDelete(DeleteView):
    @verify_position(['Service Chair', 'ec'])
    def get(self, request, *args, **kwargs):
        return super(ServiceEventDelete, self).get(request, *args, **kwargs)

    model = ServiceEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:service_c')


class ServiceEventEdit(UpdateView):
    @verify_position(['Service Chair', 'ec'])
    def get(self, request, *args, **kwargs):
        return super(ServiceEventEdit, self).get(request, *args, **kwargs)

    model = ServiceEvent
    success_url = reverse_lazy('dashboard:service_c')
    fields = ['name', 'date', 'start_time', 'end_time', 'notes']


@verify_position(['Service Chair', 'ec'])
def service_c_submission_response(request, submission_id):
    """ Renders the service chair way of responding to submissions """
    submission = ServiceSubmission.objects.get(pk=submission_id)
    form = ServiceSubmissionResponseForm(request.POST or None, initial={'status': submission.status})

    if request.method == 'POST':
        if form.is_valid():
            instance = form.cleaned_data
            submission.status = instance['status']
            submission.save()
            return HttpResponseRedirect(reverse('dashboard:service_c'))

    context = {
        'submission': submission,
        'type': 'response',
        'form': form,
    }

    return render(request, 'service-submission.html', context)


@verify_position(['Service Chair', 'ec'])
def service_c_event_add(request):
    """ Renders the service chair way of adding ServiceEvent """
    form = ServiceEventForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            try:
                semester = Semester.objects.filter(season=get_season_from(instance.date.month),
                                                   year=instance.date.year)[0]
            except IndexError:
                semester = Semester(season=get_season_from(instance.date.month),
                                    year=instance.date.year)
                semester.save()
            if instance.end_time is not None and instance.end_time < instance.start_time:
                context = {
                    'position': 'Service Chair',
                    'form': form,
                    'error_message': "Start time after end time!",
                }
                return render(request, "event-add.html", context)
            instance.semester = semester
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:service_c'))

    context = {
        'position': 'Service Chair',
        'form': form,
    }

    return render(request, 'event-add.html', context)


@verify_position(['Service Chair', 'ec'])
def service_c_hours(request):
    """ Renders the service chair way of viewing total service hours by brothers """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name")
    approved_submissions = ServiceSubmission.objects.filter(status='2')
    pending_submissions = ServiceSubmission.objects.exclude(status='2').exclude(status='3')

    approved_hours_list = []
    pending_hours_list = []

    for brother in brothers:
        approved_hours = 0
        pending_hours = 0
        for submission in approved_submissions:
            if submission.brother == brother:
                approved_hours += submission.hours
        for submission in pending_submissions:
            if submission.brother == brother:
                pending_hours += submission.hours
        approved_hours_list.append(approved_hours)
        pending_hours_list.append(pending_hours)

    brother_hours_list = zip(brothers, approved_hours_list, pending_hours_list)

    context = {
        'position': 'Service Chair',
        'brother_hours_list': brother_hours_list,
    }

    return render(request, "service-hours-list.html", context)


@verify_position(['Philanthropy Chair', 'ec'])
def philanthropy_c(request):
    """ Renders the philanthropy chair's RSVP page for different events """
    events = PhilanthropyEvent.objects.filter(semester=get_semester())
    context = {
        'events': events,
    }
    return render(request, 'philanthropy-chair.html', context)


@verify_position(['Philanthropy Chair', 'ec'])
def philanthropy_c_event(request, event_id):
    """ Renders the philanthropy event view """
    event = PhilanthropyEvent.objects.get(pk=event_id)
    brothers_rsvp = event.rsvp_brothers.all()

    context = {
        'type': 'ec-view',
        'brothers_rsvp': brothers_rsvp,
        'event': event,
    }

    return render(request, 'philanthropy-event.html', context)


@verify_position(['Philanthropy Chair', 'ec'])
def philanthropy_c_event_add(request):
    """ Renders the philanthropy chair way of adding PhilanthropyEvent """
    form = PhilanthropyEventForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            try:
                semester = Semester.objects.filter(season=get_season_from(instance.date.month),
                                                   year=instance.date.year)[0]
            except IndexError:
                semester = Semester(season=get_season_from(instance.date.month),
                                    year=instance.date.year)
                semester.save()
            if instance.end_time is not None and instance.end_time < instance.start_time:
                context = {
                    'position': 'Philanthropy Chair',
                    'form': form,
                    'error_message': "Start time after end time!",
                }
                return render(request, "event-add.html", context)
            instance.semester = semester
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:service_c'))

    context = {
        'position': 'Philanthropy Chair',
        'form': form,
    }
    return render(request, 'event-add.html', context)


class PhilanthropyEventDelete(DeleteView):
    @verify_position(['Philanthropy Chair', 'ec'])
    def get(self, request, *args, **kwargs):
        return super(PhilanthropyEventDelete, self).get(request, *args, **kwargs)

    model = PhilanthropyEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:philanthropy_c')


class PhilanthropyEventEdit(UpdateView):
    @verify_position(['Philanthropy Chair', 'ec'])
    def get(self, request, *args, **kwargs):
        return super(PhilanthropyEventEdit, self).get(request, *args, **kwargs)

    model = PhilanthropyEvent
    success_url = reverse_lazy('dashboard:philanthropy_c')
    fields = ['name', 'date', 'start_time', 'end_time', 'notes']


@verify_position(['Detail Manager'])
def detail_m(request):
    """ Renders the detail manager page"""
    return render(request, 'detail-manager.html', {})


def supplies_request(request):
    form = SuppliesForm(request.POST or None)
    context = {}

    if request.method == 'POST':
        if form.is_valid():
            form.save(commit=True)
            context['message'] = 'Thanks!'

    context['form'] = form
    return render(request, 'request-supplies.html', context)


def supplies_list(request):
    supplies = Supplies.objects.filter(done=False)
    supplies = [(e.what, e.when) for e in supplies]

    context = {'supplies': supplies}

    return render(request, 'list-supplies.html', context)


@verify_position(['Detail Manager'])
def supplies_finish(request):
    form = SuppliesFinishForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            for supply in form.cleaned_data['choices']:
                supply.done = True
                supply.save()

    context = {'form': form}
    return render(request, 'finish-supplies.html', context)


@verify_position(['Vice President', 'President'])
@transaction.atomic
def in_house(request):
    """Allows the VP to select who's living in the house"""
    form = InHouseForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            brothers = Brother.objects.filter(brother_status='1')
            brothers.update(in_house=False)
            for c in ['in_house_part', 'not_in_house_part']:
                brothers = form.cleaned_data[c]
                for b in brothers:
                    b.in_house = True
                    b.save()

    context = {'form': form}
    return render(request, 'in_house.html', context)


@verify_position(['Detail Manager'])
@transaction.atomic
def house_detail_toggle(request):
    """Selects who does house details"""
    form = HouseDetailsSelectForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            brothers = Brother.objects.filter(brother_status='1')
            brothers.update(does_house_details=False)
            for c in ['does_details_part', 'doesnt_do_details_part']:
                brothers = form.cleaned_data[c]
                for b in brothers:
                    b.does_house_details = True
                    b.save()

    context = {'form': form}
    return render(request, 'house_detail_toggle.html', context)


@verify_position(['Detail Manager'])
@transaction.atomic
def create_groups(request):
    """Create detail groups for a specific semester. Decides how many to create
    based on the group size and brothers living in the house"""
    form = CreateDetailGroups(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            num_brothers = len(Brother.objects.filter(does_house_details=True))
            num_groups = int(num_brothers / form.cleaned_data['size'])

            for i in range(num_groups):
                g = DetailGroup(semester=form.cleaned_data['semester'])
                g.save()

            return HttpResponseRedirect(reverse('dashboard:select_groups'))

    context = {'form': form}
    return render(request, 'create_groups.html', context)


@verify_position(['Detail Manager'])
@transaction.atomic
def select_groups(request):
    """Select brothers in detail groups (for this semester)"""
    form = SelectDetailGroups(request.POST or None, semester=get_semester())

    if request.method == 'POST':
        if form.is_valid():
            for gid, brothers in form.extract_groups():
                group = DetailGroup.objects.get(pk=int(gid))
                group.brothers = brothers
                group.save()

    context = {'form': form}
    return render(request, 'select_groups.html', context)


@verify_position(['Detail Manager'])
@transaction.atomic
def delete_groups(request):
    """Delete detail groups.  Can select a semester to delete form"""
    semester_form = SelectSemester(request.GET or None)
    if semester_form.is_valid():
        semester = semester_form.cleaned_data['semester']
    else:
        semester = get_semester()
    form = DeleteDetailGroup(request.POST or None, semester=semester)

    if request.method == 'POST':
        if form.is_valid():
            for g in form.cleaned_data['groups']:
                g.delete()

    context = {'form': form, 'semester_form': semester_form}

    return render(request, 'delete_groups.html', context)


@verify_position(['Detail Manager'])
@transaction.atomic
def post_thursday(request):
    """Post Thursday Details, due on the date from the form"""
    date_form = SelectDate(request.POST or None)

    if request.method == 'POST':
        if date_form.is_valid():
            brothers = Brother.objects.filter(does_house_details=True)
            details = settings.THURSDAY_DETAILS

            bros = [b for b in brothers]
            brothers = bros
            random.shuffle(details)
            random.shuffle(brothers)

            matching = zip(brothers, details)
            assigned = []
            emails = []

            for (b, d) in matching:
                detail = ThursdayDetail(
                    short_description=d['name'],
                    long_description="\n".join(d['tasks']),
                    due_date=date_form.cleaned_data['due_date'], brother=b,
                )
                detail.save()
                assigned.append(detail)
                emails.append(
                    build_thursday_detail_email(
                        detail, request.scheme + "://" + request.get_host()
                    )
                )

            det_manager_email = Position.objects.get(
                title='Detail Manager'
            ).brothers.first().user.email
            for (subject, message, to) in emails:
                send_mail(subject, message, det_manager_email, to)

    context = {'form': date_form}
    return render(request, 'post_thursday_details.html', context)


@login_required
def finish_thursday_detail(request, detail_id):
    """Marks a Thursday Detail as done, by either its owner or the detail
    manager"""
    detail = ThursdayDetail.objects.get(pk=detail_id)
    if not verify_brother(detail.brother, request.user):
        if request.user.brother not in Position.objects.get(
            title='Detail Manager'
        ).brothers.all():
            messages.error(request, "That's not your detail!")
            return HttpResponseRedirect(reverse('dashboard:home'))

    if request.method == 'POST' and not detail.done:
        detail.done = True
        detail.finished_time = datetime.datetime.now()
        detail.save()

    context = {'detail': detail}

    return render(request, 'finish_thursday_detail.html', context)


@verify_position(['Detail Manager'])
@transaction.atomic
def post_sunday(request):
    """Post Sunday Details, due on the date from the form"""
    date_form = SelectDate(request.POST or None)

    if request.method == 'POST':
        if date_form.is_valid():
            groups = DetailGroup.objects.filter(semester=get_semester())
            details = settings.SUNDAY_DETAILS

            g = [e for e in groups]
            groups = g
            random.shuffle(groups)
            random.shuffle(details)

            emails = []

            for group in groups:
                if len(details) <= 0:
                    break
                group_detail = SundayGroupDetail(
                    group=group, due_date=date_form.cleaned_data['due_date']
                )
                group_detail.save()
                for _ in range(group.size()):
                    if len(details) <= 0:
                        break
                    d = details.pop()
                    det = SundayDetail(
                        short_description=d['name'],
                        long_description="\n".join(d['tasks']),
                        due_date=date_form.cleaned_data['due_date']
                    )
                    det.save()
                    group_detail.details.add(det)
                group_detail.save()
                emails.append(
                    build_sunday_detail_email(
                        group_detail,
                        request.scheme + "://" + request.get_host()
                    )
                )

            det_manager_email = Position.objects.get(
                title='Detail Manager'
            ).brothers.first().user.email
            for (subject, message, to) in emails:
                send_mail(subject, message, det_manager_email, to)

    context = {'form': date_form}
    return render(request, 'post_sunday_details.html', context)


@login_required
def finish_sunday_detail(request, detail_id):
    groupdetail = SundayGroupDetail.objects.get(pk=detail_id)
    if request.user.brother not in groupdetail.group.brothers.all():
        if request.user.brother not in Position.objects.get(
            title='Detail Manager'
        ).brothers.all():
            messages.error(request, "That's not your detail!")
            return HttpResponseRedirect(reverse('dashboard:home'))

    form = FinishSundayDetail(request.POST or None, groupdetail=groupdetail)

    if request.method == 'POST':
        if form.is_valid():
            detail = form.cleaned_data['detail']
            detail.done = True
            detail.finished_time = datetime.datetime.now()
            detail.finished_by = request.user.brother
            detail.save()

    context = {
        'groupdetail': groupdetail,
        'details': groupdetail.details.all(),
        'form': form,
        'who': ", ".join(
            [str(b) for b in groupdetail.group.brothers.all()]
        ),
        'due': groupdetail.details.all()[0].due_date,
    }

    return render(request, 'finish_sunday_detail.html', context)


@login_required
def current_details(request):
    brother = request.user.brother
    return current_details_helper(request, brother)


@verify_position(['Detail Manager'])
def current_details_brother(request, brother_id):
    brother = Brother.objects.get(pk=brother_id)
    return current_details_helper(request, brother)


def current_details_helper(request, brother):
    if not brother.does_house_details:
        context = {
            'does_house_details': False,
            'who': str(brother),
        }
        return render(request, 'list_details.html', context)

    context = {}

    last_sunday = SundayGroupDetail.objects.filter(
        group__brothers=brother, group__semester=get_semester()
    ).order_by('-due_date').first()
    if last_sunday:
        context['last_sunday'] = last_sunday
        context['last_sunday_link'] = last_sunday.finish_link()
        context['sunday_text'] = "\n\n\n".join(
            [d.full_text() for d in last_sunday.details.all()]
        )

    last_thursday = ThursdayDetail.objects.filter(
        brother=brother
    ).order_by('-due_date').first()
    context['last_thursday'] = last_thursday
    context['last_thursday_link'] = last_thursday.finish_link()
    context['thursday_text'] = last_thursday.full_text()

    context['who'] = str(brother)
    context['does_house_details'] = True

    return render(request, 'list_details.html', context)


@login_required
def all_details(request):
    brother = request.user.brother
    return all_details_helper(request, brother)


@verify_position(['Detail Manager'])
def all_details_brother(request, brother_id):
    brother = Brother.objects.get(pk=brother_id)
    return all_details_helper(request, brother)


def all_details_helper(request, brother):
    if not brother.does_house_details:
        context = {
            'does_house_details': False,
            'who': str(brother),
        }
        return render(request, 'list_details.html', context)

    thursday_details = ThursdayDetail.objects.filter(brother=brother)

    sunday_group_details = SundayGroupDetail.objects.filter(
        group__brothers=brother, group__semester=get_semester()
    )

    context = {
        'thursday_details': thursday_details,
        'sunday_group_details': sunday_group_details,
        'does_house_details': True,
        'who': str(brother),
    }

    return render(request, 'all_details.html', context)


@verify_position(['Detail Manager'])
def all_users_details(request):
    brothers = Brother.objects.filter(brother_status='1')
    b = {e: (
            reverse('dashboard:list_details_brother', args=[e.pk]),
            reverse('dashboard:all_details_brother', args=[e.pk]),
            reverse('dashboard:detail_fine_brother', args=[e.pk]),
            calc_fines(e)
    ) for e in brothers}
    context = {'brothers': b}
    return render(request, 'all_users_details.html', context)


@verify_position(['Detail Manager'])
def detail_dates(request):
    semester_form = SelectSemester(request.GET or None)
    if semester_form.is_valid():
        semester = semester_form.cleaned_data['semester']
    else:
        semester = get_semester()

    thursday_dates = set([e.due_date for e in ThursdayDetail.objects.all()])
    thursday_dates = [
        (
            e, reverse('dashboard:details_on_date', args=[str(e)])
        ) for e in thursday_dates
    ]
    sunday_dates = set([e.due_date for e in SundayDetail.objects.all()])
    sunday_dates = [
        (
            e, reverse('dashboard:details_on_date', args=[str(e)])
        ) for e in sunday_dates
    ]

    context = {
        'semester_form': semester_form,
        'thursday_dates': thursday_dates,
        'sunday_dates': sunday_dates,
    }

    return render(request, 'details_by_date.html', context)


@verify_position(['Detail Manager'])
def details_on_date(request, date):
    d_format = "%Y-%m-%d"
    date = datetime.datetime.strptime(date, d_format).date()
    thursday_details = ThursdayDetail.objects.filter(due_date=date)
    sunday_group_details = SundayGroupDetail.objects.filter(due_date=date)

    context = {
        'date': date,
        'thursday_details': thursday_details,
        'sunday_group_details': sunday_group_details,
    }

    return render(request, 'details_on_date.html', context)
    return HttpResponse(context.values())


@login_required
def detail_fines(request):
    brother = request.user.brother
    return detail_fine_helper(request, brother)


@verify_position(['Detail Manager'])
def detail_fines_brother(request, brother_id):
    brother = Brother.objects.get(pk=brother_id)
    return detail_fine_helper(request, brother)


def detail_fine_helper(request, brother):
    if not brother.does_house_details:
        context = {
            'does_house_details': False,
            'who': str(brother),
        }
        return render(request, 'list_details.html', context)

    fine = calc_fines(brother)

    context = {'fine': fine, 'brother': brother}

    return render(request, 'detail_fines.html', context)

@verify_position(['Public Relations Chair', 'Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def public_relations_c(request):
    return render(request, 'public-relations-chair.html', {})
