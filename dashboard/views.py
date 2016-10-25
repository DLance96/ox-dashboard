import csv

from django.contrib import messages
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import *
from django.views.generic.edit import UpdateView, DeleteView

import utils
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


def contact_list(request):
    """ Renders contact info page """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name")

    context = {
        'brothers': brothers,
    }
    return render(request, 'contact-list.html', context)


def emergency_contact_list(request):
    """ Renders emergency contact info page """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name")

    context = {
        'brothers': brothers,
    }
    return render(request, 'emergency-contact-list.html', context)


def event_list(request):
    """Renders all the semester events"""
    chapter_events = ChapterEvent.objects.filter(semester=utils.get_semester()).order_by("date")
    recruitment_events = RecruitmentEvent.objects.filter(semester=utils.get_semester()).order_by("date")
    service_events = ServiceEvent.objects.filter(semester=utils.get_semester()).order_by("date")
    philanthropy_events = PhilanthropyEvent.objects.filter(semester=utils.get_semester()).order_by("date")

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
    chapter_events = ChapterEvent.objects.filter(semester=utils.get_semester()).order_by("date")

    excuses_pending = Excuse.objects.filter(brother=brother, event__semester=utils.get_semester(),
                                            status='0').order_by("event__date")
    excuses_approved = Excuse.objects.filter(brother=brother, event__semester=utils.get_semester(),
                                             status='1').order_by("event__date")
    excuses_denied = Excuse.objects.filter(brother=brother, event__semester=utils.get_semester(),
                                           status='2').order_by("event__date")
    excuses_not_mandatory = Excuse.objects.filter(brother=brother, event__semester=utils.get_semester(),
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
            if event.attendees.filter(id=brother.id):
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
        operational_meetings = CommitteeMeetingEvent.objects.filter(semester=utils.get_semester(),
                                                                    committee=committee_reverse[
                                                                        brother.get_operational_committee_display()]) \
            .order_by("datetime")
    if brother.get_standing_committee_display() != 'Unassigned':
        standing_meetings = CommitteeMeetingEvent.objects.filter(semester=utils.get_semester(),
                                                                 committee=committee_reverse[
                                                                     brother.get_standing_committee_display()]) \
            .order_by("datetime")

    current_season = utils.get_season()
    if current_season is '0':
        recruitment_events = RecruitmentEvent.objects.filter(semester__season='0', semester__year=utils.get_year()) \
            .order_by("date")
        recruitment_events_next = RecruitmentEvent.objects.filter(semester__season='2', semester__year=utils.get_year()) \
            .order_by("date")
    else:
        recruitment_events = RecruitmentEvent.objects.filter(semester__season='2', semester__year=utils.get_year()) \
            .order_by("date")
        recruitment_events_next = RecruitmentEvent.objects.filter(semester__season='0', semester__year=utils.get_year()) \
            .order_by("date")
    pnms = PotentialNewMember.objects.filter(Q(primary_contact=brother) |
                                             Q(secondary_contact=brother) |
                                             Q(tertiary_contact=brother)).order_by("last_name")
    service_events = ServiceEvent.objects.filter(semester=utils.get_semester()).order_by("date")
    # Service submissions
    submissions_pending = ServiceSubmission.objects.filter(brother=brother, semester=utils.get_semester(),
                                                           status='0').order_by("date")
    submissions_submitted = ServiceSubmission.objects.filter(brother=brother, semester=utils.get_semester(),
                                                             status='1').order_by("date")
    submissions_approved = ServiceSubmission.objects.filter(brother=brother, semester=utils.get_semester(),
                                                            status='2').order_by("date")
    submissions_denied = ServiceSubmission.objects.filter(brother=brother, semester=utils.get_semester(),
                                                          status='3').order_by("date")

    hours_pending = 0
    for submission in submissions_pending:
        hours_pending += submission.hours
    for submission in submissions_submitted:
        hours_pending += submission.hours

    hours_approved = 0
    for submission in submissions_approved:
        hours_approved += submission.hours

    philanthropy_events = PhilanthropyEvent.objects.filter(semester=utils.get_semester()) \
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
        if not utils.verify_brother(brother, request.user):
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
        if not utils.verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ExcuseEdit, self).get(request, *args, **kwargs)

    model = Excuse
    success_url = reverse_lazy('dashboard:brother')
    fields = ['description']


class BrotherEdit(UpdateView):
    def get(self, request, *args, **kwargs):
        brother = Brother.objects.get(pk=self.kwargs['pk'])
        if not utils.verify_brother(brother, request.user):
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
    events = RecruitmentEvent.objects.filter(semester=utils.get_season()).order_by("date").all()

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
            semester = utils.get_semester()
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
        if not utils.verify_brother(brother, request.user):
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
        if not utils.verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ServiceSubmissionEdit, self).get(request, *args, **kwargs)

    model = ServiceSubmission
    success_url = reverse_lazy('dashboard:brother')
    fields = ['name', 'date', 'description', 'hours', 'status']


def president(request):
    """ Renders the President page and all relevant information """
    if not utils.verify_president(request.user):
        messages.error(request, "President Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    return render(request, 'president.html', {})


def vice_president(request):
    """ Renders the Vice President page and all relevant information, primarily committee related """
    if not utils.verify_vice_president(request.user):
        messages.error(request, "Vice President Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    committee_meetings = CommitteeMeetingEvent.objects.filter(semester=utils.get_semester()).order_by("datetime")

    context = {
        'committee_meetings': committee_meetings,
    }

    return render(request, 'vice-president.html', context)


def vice_president_committee_assignments(request):
    """Renders Committee assignment update page for the Vice President"""
    if not utils.verify_vice_president(request.user):
        messages.error(request, "Vice President Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    form_list = []
    brothers = Brother.objects.exclude(brother_status='2')
    for brother in brothers:
        new_form = CommitteeForm(request.POST or None, initial={'standing_committee': brother.standing_committee,
                                                                'operational_committee': brother.operational_committee},
                                 prefix=brother.id)
        form_list.append(new_form)

    brother_forms = zip(brothers, form_list)

    if request.method == 'POST':
        if utils.forms_is_valid(form_list):
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


def vice_president_committee_meeting_add(request):
    """ Renders the committee meeting add page """
    if not utils.verify_vice_president(request.user):
        messages.error(request, "Vice President Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    form = CommitteeMeetingForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)

            try:
                semester = Semester.objects.filter(season=utils.get_season_from(instance.datetime.month),
                                                   year=instance.datetime.year)[0]
            except IndexError:
                semester = Semester(season=utils.get_season_from(instance.datetime.month),
                                    year=instance.datetime.year)
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
    def get(self, request, *args, **kwargs):
        if not utils.verify_vice_president(request.user):
            messages.error(request, "Vice President Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(CommitteeMeetingDelete, self).get(request, *args, **kwargs)

    model = CommitteeMeetingEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:vice_president')


class CommitteeMeetingEdit(UpdateView):
    def get(self, request, *args, **kwargs):
        if not utils.verify_vice_president(request.user):
            messages.error(request, "Vice President Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(CommitteeMeetingEdit, self).get(request, *args, **kwargs)

    model = CommitteeMeetingEvent
    success_url = reverse_lazy('dashboard:vice_president')
    fields = ['datetime', 'semester', 'committee', 'minutes']


def treasurer(request):
    """ Renders all the transactional information on the site for the treasurer """
    if not utils.verify_treasurer(request.user):
        messages.error(request, "Treasurer Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))
    return render(request, 'treasurer.html', {})


def secretary(request):
    """ Renders the secretary page giving access to excuses and ChapterEvents """
    print utils.verify_secretary(request.user)
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    excuses = Excuse.objects.filter(event__semester=utils.get_semester(), status='0').order_by("event__date")
    events = ChapterEvent.objects.filter(semester=utils.get_semester()).order_by("date")

    context = {
        'excuses': excuses,
        'events': events,
    }
    return render(request, 'secretary.html', context)


def secretary_attendance(request):
    """ Renders the secretary view for chapter attendance """
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brothers = Brother.objects.exclude(brother_status='2').order_by('last_name')
    events = ChapterEvent.objects.filter(semester=utils.get_semester(), mandatory=True)\
        .exclude(date__gt=datetime.date.today())
    excuses = Excuse.objects.filter(event__semester=utils.get_semester(), status='1')
    events_excused_list = []
    events_unexcused_list = []

    for brother in brothers:
        events_excused = 0
        events_unexcused = 0
        for event in events:
            if not event.attendees.filter(id=brother.id).exists():
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


def secretary_event(request, event_id):
    """ Renders the attendance sheet for any event """
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    event = ChapterEvent.objects.get(pk=event_id)
    brothers = Brother.objects.exclude(brother_status='2').order_by('last_name')
    form_list = []
    for brother in brothers:
        if event.attendees.filter(id=brother.id):
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
        if utils.forms_is_valid(form_list):
            for counter, form in enumerate(form_list):
                instance = form.cleaned_data
                if instance['present'] is True:
                    event.attendees.add(brothers[counter])
                    event.save()
                if instance['present'] is False:
                    event.attendees.remove(brothers[counter])
                    event.save()
            return HttpResponseRedirect(reverse('dashboard:secretary'))

    context = {
        'type': 'attendance',
        'brother_form_list': form_list,
        'event': event,
    }
    return render(request, "chapter-event.html", context)


def secretary_excuse(request, excuse_id):
    """ Renders Excuse response form """
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

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


def secretary_all_excuses(request):
    """ Renders Excuse """
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    excuses = Excuse.objects.order_by('brother__last_name','event__date')

    context = {
        'excuses': excuses
    }
    return render(request, 'secretary_excuses.html', context)


def secretary_event_view(request, event_id):
    """ Renders the Secretary way of viewing old events """
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    event = ChapterEvent.objects.get(pk=event_id)
    attendees = event.attendees.all().order_by("last_name")

    context = {
        'type': 'ec-view',
        'attendees': attendees,
        'event': event,
    }
    return render(request, "chapter-event.html", context)


def secretary_brother_list(request):
    """ Renders the Secretary way of viewing brothers """
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brothers = Brother.objects.exclude(brother_status='2')
    context = {
        'position': 'Secretary',
        'brothers': brothers
    }
    return render(request, "brother-list.html", context)


def secretary_brother_view(request, brother_id):
    """ Renders the Secretary way of viewing a brother """
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brother = Brother.objects.get(pk=brother_id)
    context = {
        'brother': brother
    }
    return render(request, "brother-view.html", context)


def secretary_brother_add(request):
    """ Renders the Secretary way of viewing a brother """
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

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
    def get(self, request, *args, **kwargs):
        if not utils.verify_secretary(request.user):
            messages.error(request, "Secretary Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(SecretaryBrotherEdit, self).get(request, *args, **kwargs)

    model = Brother
    success_url = reverse_lazy('dashboard:secretary_brother_list')
    fields = ['first_name', 'last_name', 'roster_number', 'semester_joined', 'school_status', 'brother_status',
              'major', 'minor', 't_shirt_size', 'case_ID', 'birthday', 'hometown', 'phone_number',
              'emergency_contact_phone_number', 'emergency_contact', 'standing_committee', 'operational_committee',
              'room_number', 'address']


class SecretaryBrotherDelete(DeleteView):
    def get(self, request, *args, **kwargs):
        if not utils.verify_secretary(request.user):
            messages.error(request, "Secretary Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(SecretaryBrotherDelete, self).get(request, *args, **kwargs)

    model = Brother
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:secretary')


def secretary_event_add(request):
    """ Renders the Secretary way of adding ChapterEvents """
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    form = ChapterEventForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            try:
                semester = Semester.objects.filter(season=utils.get_season_from(instance.date.month),
                                                   year=instance.date.year)[0]
            except IndexError:
                semester = Semester(season=utils.get_season_from(instance.date.month),
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
    def get(self, request, *args, **kwargs):
        if not utils.verify_secretary(request.user):
            messages.error(request, "Secretary Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ChapterEventEdit, self).get(request, *args, **kwargs)

    model = ChapterEvent
    success_url = reverse_lazy('dashboard:secretary')
    fields = ['name', 'mandatory', 'date', 'start_time', 'end_time', 'minutes', 'notes']


class ChapterEventDelete(DeleteView):
    def get(self, request, *args, **kwargs):
        if not utils.verify_secretary(request.user):
            messages.error(request, "Secretary Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ChapterEventDelete, self).get(request, *args, **kwargs)

    model = ChapterEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:secretary')


def secretary_all_events(request):
    """ Renders a secretary view with all the ChapterEvent models ordered by date grouped by semester """
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

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


def secretary_positions(request):
    """ Renders all of the positions currently in the chapter """
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    # Checking to make sure all of the EC and dashboard required positions are setup
    for position in utils.ec:
        if not Position.objects.filter(title=position).exists():
            new_position = Position(title=position, ec=True)
            new_position.save()
    for position in utils.non_ec:
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


def secretary_position_add(request):
    """ Renders the Secretary way of viewing a brother """
    if not utils.verify_secretary(request.user):
        messages.error(request, "Secretary Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

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
    def get(self, request, *args, **kwargs):
        if not utils.verify_secretary(request.user):
            messages.error(request, "Secretary Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(PositionEdit, self).get(request, *args, **kwargs)

    model = Position
    success_url = reverse_lazy('dashboard:secretary_positions')
    fields = ['brother']


class PositionDelete(DeleteView):
    def get(self, request, *args, **kwargs):
        if not utils.verify_secretary(request.user):
            messages.error(request, "Secretary Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(PositionDelete, self).get(request, *args, **kwargs)

    model = Position
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:secretary_positions')


def marshal(request):
    """ Renders the marshal page listing all the candidates and relevant information to them """
    if not utils.verify_marshal(request.user):
        messages.error(request, "Marshal Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    candidates = Brother.objects.filter(brother_status='0').order_by("last_name")
    events = ChapterEvent.objects.filter(semester=utils.get_semester()).exclude(date__gt=datetime.date.today())
    excuses = Excuse.objects.filter(event__semester=utils.get_semester(), status='1')
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
            if not event.attendees.filter(id=candidate.id).exists():
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


def marshal_candidate(request, brother_id):
    """ Renders the marshal page to view candidate info """
    if not utils.verify_marshal(request.user):
        messages.error(request, "Marshal Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brother = Brother.objects.get(pk=brother_id)
    context = {
        'brother': brother
    }
    return render(request, "brother-view.html", context)


def marshal_candidate_add(request):
    """ Renders the Marshal way of viewing a candidate """
    if not utils.verify_marshal(request.user):
        messages.error(request, "Marshal Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

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
    def get(self, request, *args, **kwargs):
        if not utils.verify_marshal(request.user):
            messages.error(request, "Marshal Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(CandidateEdit, self).get(request, *args, **kwargs)

    model = Brother
    success_url = reverse_lazy('dashboard:marshal')
    fields = ['first_name', 'last_name', 'roster_number', 'semester_joined', 'school_status', 'brother_status',
              'major', 'minor', 't_shirt_size', 'case_ID', 'birthday', 'hometown', 'phone_number',
              'emergency_contact_phone_number', 'emergency_contact', 'room_number',
              'address']


class CandidateDelete(DeleteView):
    def get(self, request, *args, **kwargs):
        if not utils.verify_marshal(request.user):
            messages.error(request, "Marshal Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(CandidateDelete, self).get(request, *args, **kwargs)

    model = Brother
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:marshal')


def scholarship_c(request):
    """ Renders the Scholarship page listing all brother gpas and study table attendance """
    if not utils.verify_scholarship_chair(request.user):
        messages.error(request, "Scholarship Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    events = StudyTableEvent.objects.filter(semester=utils.get_semester()).order_by("date")

    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name")
    plans = []

    for brother in brothers:
        plan = ScholarshipReport.objects.filter(semester=utils.get_semester(), brother__id=brother.id)
        if plan.exists():
            plan = plan[0]
        else:
            plan = ScholarshipReport(brother=brother, semester=utils.get_semester())
            plan.save()
        plans.append(plan)

    brother_plans = zip(brothers, plans)

    context = {
        'events': events,
        'brother_plans': brother_plans,
    }
    return render(request, "scholarship-chair.html", context)


def scholarship_c_event(request, event_id):
    """ Renders the scholarship chair way of view StudyTables """
    if not utils.verify_scholarship_chair(request.user):
        messages.error(request, "Scholarship Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    event = StudyTableEvent.objects.get(pk=event_id)
    brothers = Brother.objects.exclude(brother_status='2')
    brother_form_list = []

    for brother in brothers:
        if event.attendees.filter(id=brother.id):
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
        if utils.forms_is_valid(brother_form_list):
            for counter, form in enumerate(brother_form_list):
                instance = form.cleaned_data
                if instance['present'] is True:
                    event.attendees.add(brothers[counter])
                    event.save()
                if instance['present'] is False:
                    event.attendees.remove(brothers[counter])
                    event.save()
            return HttpResponseRedirect(reverse('dashboard:scholarship_c'))

    context = {
        'type': 'attendance',
        'brother_form_list': brother_form_list,
        'event': event,
    }
    return render(request, "studytable-event.html", context)


def scholarship_c_event_add(request):
    """ Renders the scholarship chair way of adding StudyTableEvents """
    if not utils.verify_scholarship_chair(request.user):
        messages.error(request, "Scholarship Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    form = StudyTableEventForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            try:
                semester = Semester.objects.filter(season=utils.get_season_from(instance.date.month),
                                                   year=instance.date.year)[0]
            except IndexError:
                semester = Semester(season=utils.get_season_from(instance.date.month),
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
    def get(self, request, *args, **kwargs):
        if not utils.verify_scholarship_chair(request.user):
            messages.error(request, "Scholarship Chair Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(StudyEventDelete, self).get(request, *args, **kwargs)

    model = StudyTableEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:scholarship_c')


class StudyEventEdit(UpdateView):
    def get(self, request, *args, **kwargs):
        if not utils.verify_scholarship_chair(request.user):
            messages.error(request, "Scholarship Chair Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(StudyEventEdit, self).get(request, *args, **kwargs)

    model = StudyTableEvent
    success_url = reverse_lazy('dashboard:scholarship_c')
    fields = ['date', 'start_time', 'end_time', 'notes']


def scholarship_c_plan(request, plan_id):
    """Renders Scholarship Plan page for the Scholarship Chair"""
    if not utils.verify_scholarship_chair(request.user):
        messages.error(request, "Scholarship Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    plan = ScholarshipReport.objects.get(pk=plan_id)
    events = StudyTableEvent.objects.filter(semester=utils.get_semester()).exclude(date__gt=datetime.date.today())
    study_tables_attended = 0
    study_tables_count = len(events)

    for event in events:
        if event.attendees.filter(id=plan.brother.id).exists():
            study_tables_attended += 1

    context = {
        'type': 'scholarship-chair',
        'plan': plan,
        'study_tables_count': study_tables_count,
        'study_tables_attended': study_tables_attended,
    }

    return render(request, 'scholarship-report.html', context)


def scholarship_c_gpa(request):
    """Renders Scholarship Gpa update page for the Scholarship Chair"""
    if not utils.verify_scholarship_chair(request.user):
        messages.error(request, "Scholarship Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    plans = ScholarshipReport.objects.filter(semester=utils.get_semester()).order_by("brother__last_name")
    form_list = []

    for plan in plans:
        new_form = GPAForm(request.POST or None, initial={'cum_GPA': plan.cumulative_gpa,
                                                          'past_GPA': plan.past_semester_gpa}, prefix=plan.id)
        form_list.append(new_form)

    form_plans = zip(form_list, plans)

    if request.method == 'POST':
        if utils.forms_is_valid(form_list):
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
    def get(self, request, *args, **kwargs):
        if not utils.verify_scholarship_chair(request.user):
            messages.error(request, "Scholarship Chair Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ScholarshipReportEdit, self).get(request, *args, **kwargs)

    model = ScholarshipReport
    success_url = reverse_lazy('dashboard:scholarship_c')
    fields = ['cumulative_gpa', 'past_semester_gpa', 'scholarship_plan', 'active']


def recruitment_c(request):
    """ Renders Scholarship chair page with events for the current and following semester """
    if not utils.verify_recruitment_chair(request.user):
        messages.error(request, "Recruitment Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    current_season = utils.get_season()
    if current_season is '0':
        semester_events = RecruitmentEvent.objects.filter(semester__season='0', semester__year=utils.get_year())
        semester_events_next = RecruitmentEvent.objects.filter(semester__season='2', semester__year=utils.get_year())
    else:
        semester_events = RecruitmentEvent.objects.filter(semester__season='2', semester__year=utils.get_year())
        semester_events_next = RecruitmentEvent.objects.filter(semester__season='0', semester__year=utils.get_year())

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


def recruitment_c_rush_attendance(request):
    """ Renders Scholarship chair page with rush attendance """
    if not utils.verify_recruitment_chair(request.user):
        messages.error(request, "Recruitment Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name")
    events = RecruitmentEvent.objects.filter(semester=utils.get_semester(), rush=True) \
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


def recruitment_c_pnm(request, pnm_id):
    """ Renders PNM view for recruitment chair """
    if not utils.verify_recruitment_chair(request.user):
        messages.error(request, "Recruitment Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    pnm = PotentialNewMember.objects.get(pk=pnm_id)
    events = RecruitmentEvent.objects.filter(semester=utils.get_semester()).order_by("date").all()

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


def recruitment_c_pnm_add(request):
    """ Renders the recruitment chair way of adding PNMs """
    if not utils.verify_recruitment_chair(request.user):
        messages.error(request, "Recruitment Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

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
    def get(self, request, *args, **kwargs):
        if not utils.verify_recruitment_chair(request.user):
            messages.error(request, "Recruitment Chair Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(PnmDelete, self).get(request, *args, **kwargs)

    model = PotentialNewMember
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:recruitment_c')


class PnmEdit(UpdateView):
    def get(self, request, *args, **kwargs):
        if not utils.verify_recruitment_chair(request.user):
            messages.error(request, "Recruitment Chair Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(PnmEdit, self).get(request, *args, **kwargs)

    model = PotentialNewMember
    success_url = reverse_lazy('dashboard:recruitment_c')
    fields = ['first_name', 'last_name', 'case_ID', 'phone_number', 'primary_contact', 'secondary_contact',
              'tertiary_contact', 'notes']


def recruitment_c_event(request, event_id):
    """ Renders the recruitment chair way of view RecruitmentEvents """
    if not utils.verify_recruitment_chair(request.user):
        messages.error(request, "Recruitment Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

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
        if utils.forms_is_valid(pnm_form_list) and utils.forms_is_valid(brother_form_list):
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


def recruitment_c_event_add(request):
    """ Renders the recruitment chair way of adding RecruitmentEvents """
    if not utils.verify_recruitment_chair(request.user):
        messages.error(request, "Recruitment Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    form = RecruitmentEventForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            try:
                semester = Semester.objects.filter(season=utils.get_season_from(instance.date.month),
                                                   year=instance.date.year)[0]
            except IndexError:
                semester = Semester(season=utils.get_season_from(instance.date.month),
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
    def get(self, request, *args, **kwargs):
        if not utils.verify_recruitment_chair(request.user):
            messages.error(request, "Recruitment Chair Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(RecruitmentEventDelete, self).get(request, *args, **kwargs)

    model = RecruitmentEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:recruitment_c')


class RecruitmentEventEdit(UpdateView):
    def get(self, request, *args, **kwargs):
        if not utils.verify_recruitment_chair(request.user):
            messages.error(request, "Recruitment Chair Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(RecruitmentEventEdit, self).get(request, *args, **kwargs)

    model = RecruitmentEvent
    success_url = reverse_lazy('dashboard:recruitment_c')
    fields = ['name', 'rush', 'date', 'start_time', 'end_time', 'notes']


def service_c(request):
    """ Renders the service chair page with service submissions """
    if not utils.verify_service_chair(request.user):
        messages.error(request, "Service Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    events = ServiceEvent.objects.filter(semester=utils.get_semester())
    submissions_pending = ServiceSubmission.objects.filter(semester=utils.get_semester(), status='0').order_by("date")

    submissions_submitted = ServiceSubmission.objects.filter(semester=utils.get_semester(), status='1').order_by(
        "date")

    hours_pending = 0
    for submission in submissions_pending:
        hours_pending += submission.hours
    for submission in submissions_submitted:
        hours_pending += submission.hours

    hours_approved = 0
    submissions_approved = ServiceSubmission.objects.filter(semester=utils.get_semester(), status='2')
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


def service_c_event(request, event_id):
    """ Renders the service chair way of adding ServiceEvent """
    if not utils.verify_service_chair(request.user):
        messages.error(request, "Service Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    event = ServiceEvent.objects.get(pk=event_id)
    brothers = Brother.objects.exclude(brother_status='2')
    brothers_rsvp = event.rsvp_brothers.all()
    form_list = []

    for brother in brothers:
        if event.attendees.filter(id=brother.id):
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
        if utils.forms_is_valid(form_list):
            for counter, form in enumerate(form_list):
                instance = form.cleaned_data
                if instance['present'] is True:
                    event.attendees.add(brothers[counter])
                    event.save()
                if instance['present'] is False:
                    event.attendees.remove(brothers[counter])
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
    def get(self, request, *args, **kwargs):
        if not utils.verify_service_chair(request.user):
            messages.error(request, "Service Chair Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ServiceEventDelete, self).get(request, *args, **kwargs)

    model = ServiceEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:service_c')


class ServiceEventEdit(UpdateView):
    def get(self, request, *args, **kwargs):
        if not utils.verify_service_chair(request.user):
            messages.error(request, "Service Chair Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(ServiceEventEdit, self).get(request, *args, **kwargs)

    model = ServiceEvent
    success_url = reverse_lazy('dashboard:service_c')
    fields = ['name', 'date', 'start_time', 'end_time', 'notes']


def service_c_submission_response(request, submission_id):
    """ Renders the service chair way of responding to submissions """
    if not utils.verify_service_chair(request.user):
        messages.error(request, "Service Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

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


def service_c_event_add(request):
    """ Renders the service chair way of adding ServiceEvent """
    if not utils.verify_service_chair(request.user):
        messages.error(request, "Service Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    form = ServiceEventForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            try:
                semester = Semester.objects.filter(season=utils.get_season_from(instance.date.month),
                                                   year=instance.date.year)[0]
            except IndexError:
                semester = Semester(season=utils.get_season_from(instance.date.month),
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


def service_c_hours(request):
    """ Renders the service chair way of viewing total service hours by brothers """
    if not utils.verify_service_chair(request.user):
        messages.error(request, "Service Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

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


def philanthropy_c(request):
    """ Renders the philanthropy chair's RSVP page for different events """
    if not utils.verify_philanthropy_chair(request.user):
        messages.error(request, "Philanthropy Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    events = PhilanthropyEvent.objects.filter(semester=utils.get_semester())
    context = {
        'events': events,
    }
    return render(request, 'philanthropy-chair.html', context)


def philanthropy_c_event(request, event_id):
    """ Renders the philanthropy event view """
    if not utils.verify_philanthropy_chair(request.user):
        messages.error(request, "Philanthropy Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    event = PhilanthropyEvent.objects.get(pk=event_id)
    brothers_rsvp = event.rsvp_brothers.all()

    context = {
        'type': 'ec-view',
        'brothers_rsvp': brothers_rsvp,
        'event': event,
    }

    return render(request, 'philanthropy-event.html', context)


def philanthropy_c_event_add(request):
    """ Renders the philanthropy chair way of adding PhilanthropyEvent """
    if not utils.verify_philanthropy_chair(request.user):
        messages.error(request, "Philanthropy Chair Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

    form = PhilanthropyEventForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            try:
                semester = Semester.objects.filter(season=utils.get_season_from(instance.date.month),
                                                   year=instance.date.year)[0]
            except IndexError:
                semester = Semester(season=utils.get_season_from(instance.date.month),
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
    def get(self, request, *args, **kwargs):
        if not utils.verify_philanthropy_chair(request.user):
            messages.error(request, "Philanthropy Chair Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(PhilanthropyEventDelete, self).get(request, *args, **kwargs)

    model = PhilanthropyEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:philanthropy_c')


class PhilanthropyEventEdit(UpdateView):
    def get(self, request, *args, **kwargs):
        if not utils.verify_philanthropy_chair(request.user):
            messages.error(request, "Philanthropy Chair Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(PhilanthropyEventEdit, self).get(request, *args, **kwargs)

    model = PhilanthropyEvent
    success_url = reverse_lazy('dashboard:philanthropy_c')
    fields = ['name', 'date', 'start_time', 'end_time', 'notes']


def detail_m(request):
    """ Renders the detail manager page"""
    if not utils.verify_detail_manager(request.user):
        messages.error(request, "Detail Manager Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))

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


def supplies_finish(request):
    if not utils.verify_detail_manager(request.user):
        messages.error(request, "Detail Manager Access Denied!")
        return HttpResponseRedirect(reverse('dashboard:home'))
    form = SuppliesFinishForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            for supply in form.cleaned_data['choices']:
                supply.done = True
                supply.save()

    context = {'form': form}
    return render(request, 'finish-supplies.html', context)
