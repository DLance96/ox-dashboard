import csv
import random

from django.contrib import messages, auth
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import *
from django.views.generic.edit import UpdateView, DeleteView
from django.db import transaction
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist


from .utils import *
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
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Cannot change password if you are not logged in")
        return HttpResponseRedirect(reverse('dashboard:home'))
    brother = request.user.brother
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

    context = photo_context(Photo)
    recruitment_events = RecruitmentEvent.objects \
                                         .filter(semester=get_semester()) \
                                         .filter(date__gte=datetime.date.today()) \
                                         .order_by("date")
    context.update({
        'recruitment_events': recruitment_events,
    })

    return render(request, 'home.html', context)


def brother_info_list(request):
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in")
        return HttpResponseRedirect(reverse('dashboard:home'))

    """ Renders brother info page """
    brothers = Brother.objects.order_by("brother_status", "last_name", "first_name")
    brother_count = Brother.objects.filter(brother_status="1").count()
    candidate_count = Brother.objects.filter(brother_status="0").count()

    context = {
        'brothers': brothers,
        'brother_count': brother_count,
        'candidate_count': candidate_count,
    }
    return render(request, 'brother-info-list.html', context)


@login_required
def contact_list(request):
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in")
        return HttpResponseRedirect(reverse('dashboard:home'))

    """ Renders contact info page """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name", "first_name")

    context = {
        'brothers': brothers,
    }
    return render(request, 'contact-list.html', context)


@login_required
def emergency_contact_list(request):
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in")
        return HttpResponseRedirect(reverse('dashboard:home'))

    """ Renders emergency contact info page """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name", "first_name")

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
    hs_events = HealthAndSafetyEvent.objects.filter(semester=get_semester()).order_by("date")

    context = {
        'chapter_events': chapter_events,
        'recruitment_events': recruitment_events,
        'service_events': service_events,
        'philanthropy_events': philanthropy_events,
        'hs_events': hs_events,
        'type': 'general'
    }

    return render(request, "event-list.html", context)


def classes(request, department=None, number=None, brother=None):
    if request.user.brother in Position.objects.get(title='Scholarship Chair').brothers.all():
        view = "scholarship"
    else:
        view = ""
    classes_taken = Classes.objects.all().order_by('department', 'number')
    if department is not None:
        classes_taken = classes_taken.filter(department=department)
    if brother is not None:
        classes_taken = classes_taken.filter(brothers=brother)
        if isinstance(brother, str):
            brother = int(brother)
        if request.user.brother.pk == brother:
            view = "brother"
    if number is not None:
        classes_taken = classes_taken.filter(number=number)

    if request.method == 'POST':
        if 'filter' in request.POST:
            form = request.POST
            department = ('department', form.get('department'))
            brother = ('brother', form.get('brother'))
            number = ('number', form.get('class_number'))
            kwargs = dict((arg for arg in [department, number, brother] if arg[1] != ""))

            return HttpResponseRedirect(reverse('dashboard:classes', kwargs=kwargs))
        elif 'unadd_self' in request.POST:
            form = request.POST
            class_taken = Classes.objects.get(pk=form.get('class'))
            class_taken.brothers.remove(request.user.brother)
            if not class_taken.brothers.exists():
                class_taken.delete()


    context = {
        'classes_taken': classes_taken,
        'departments': Classes.objects.all().values_list('department', flat=True).distinct,
        'brothers': Brother.objects.all(),
        'filter_department': department,
        'filter_number': number,
        'filter_brother': brother,
        'view': view,
    }

    return render(request, "classes.html", context)


def classes_add(request):
    form = ClassTakenForm(request.POST or None)

    brother = request.user.brother

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.department = instance.department.upper()
            class_taken, created = Classes.objects.get_or_create(department=instance.department, number=instance.number)
            class_taken.brothers.add(brother)
            brother_grades = Grade(grade=form.cleaned_data['grade'], class_taken=class_taken, brother=brother)
            brother_grades.save()
            class_taken.save()
            return HttpResponseRedirect(reverse('dashboard:classes'), brother.pk)

    context = {
        'form': form,
        'brother': brother,
        'title': 'Add a Class',
    }

    return render(request, "model-add.html", context)


class ClassesDelete(DeleteView):
    @verify_position(['Scholarship Chair', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ClassesDelete, self).get(request, *args, **kwargs)

    model = Classes
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:classes')


def create_report(request):
    brother = request.user.brother
    positions = brother.position_set.exclude(title__in=['Adviser'])

    form = ReportForm(request.POST or None)

    if Position.objects.get(title='Secretary') in positions:
        form.fields["position"].queryset = Position.objects.exclude(title__in=['Adviser'])
    else:
        form.fields["position"].queryset = positions

    if request.method == "POST":
        if form.is_valid():
            instance = form.save(commit=False)
            instance.brother = brother
            instance.save()
            if Position.objects.get(title='Secretary') in positions:
                return HttpResponseRedirect(reverse('dashboard:secretary_agenda'))
            else:
                return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'form': form,
        'brother': brother,
        'title': 'Submit Officer Report or Communication'
    }

    return render(request, "model-add.html", context)


class DeleteReport(DeleteView):
    def get(self, request, *args, **kwargs):
        report = Report.objects.get(pk=self.kwargs['pk'])
        brother = report.brother
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(DeleteReport, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.GET.get('next')

    model = Report
    template_name = 'dashboard/base_confirm_delete.html'


class EditReport(UpdateView):
    def get(self, request, *args, **kwargs):
        report = Report.objects.get(pk=self.kwargs['pk'])
        brother = report.brother
        if not verify_brother(brother, request.user):
            messages.error(request, "Brother Access Denied!")
            return HttpResponseRedirect(reverse('dashboard:home'))
        return super(EditReport, self).get(request, *args, **kwargs)

    def get_form(self):
        form = super().get_form()
        form.fields["position"].queryset = Report.objects.get(pk=self.kwargs['pk']).brother.position_set.exclude(title__in=['Adviser'])
        return form


    model = Report
    success_url = reverse_lazy('dashboard:brother')
    fields = ['position', 'information']


def brother_view(request):
    """ Renders the brother page of current user showing all standard brother information """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother needs to be logged in before viewing brother portal")
        return HttpResponseRedirect(reverse('dashboard:home'))
    brother = request.user.brother
    hs_events = HealthAndSafetyEvent.objects.filter(semester=get_semester()).order_by("date")
    chapter_events = ChapterEvent.objects.filter(semester=get_semester()).order_by("date")

    # creates lists of events that were pending and approved for the current brother
    excuses = Excuse.objects.filter(brother=brother, event__semester=get_semester()).order_by("event__date")
    excuses_pending = excuses.filter(status='0').values_list('event', flat=True)
    excuses_approved = excuses.filter(status='1').values_list('event', flat=True)

    operational_committees = []
    standing_committees = []
    meetings = []

    for committee in brother.committee_set.all():
        if committee.in_standing():
            standing_committees.append(committee)
        elif committee.in_operational():
            operational_committees.append(committee)
        for meeting in committee.meetings.all():
            meetings.append(meeting)

    # creates a list of tuples: (event, attendance type)
    chapter_attendance = create_attendance_list(chapter_events, excuses_pending, excuses_approved, brother)

    hs_attendance = create_attendance_list(hs_events, excuses_pending, excuses_approved, brother)

    current_season = get_season()
    if current_season == '0':
        recruitment_events = RecruitmentEvent.objects.filter(semester__season='0', semester__year=get_year()) \
            .order_by("date")
        recruitment_events_next = RecruitmentEvent.objects.filter(semester__season='2', semester__year=get_year()) \
            .order_by("date")
    else:
        recruitment_events = RecruitmentEvent.objects.filter(semester__season='2', semester__year=get_year()) \
            .order_by("date")
        recruitment_events_next = RecruitmentEvent.objects.filter(semester__season='0', semester__year=get_year()) \
            .order_by("date")
    recruitment_attendance = create_attendance_list(recruitment_events, excuses_pending, excuses_approved, brother)

    pnms = PotentialNewMember.objects.filter(Q(primary_contact=brother) |
                                             Q(secondary_contact=brother) |
                                             Q(tertiary_contact=brother)).order_by("last_name", "first_name")

    service_events = ServiceEvent.objects.filter(semester=get_semester()).order_by("date")
    service_attendance = create_attendance_list(service_events, excuses_pending, excuses_approved, brother)

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

    philanthropy_attendance = create_attendance_list(philanthropy_events, excuses_pending, excuses_approved, brother)

    mab = None

    if brother.brother_status == '0':
        mab = [x.brother for x in brother.candidate_mab.filter(completed=False)]
    elif brother.brother_status == '1':
        mab = [x.candidate for x in brother.brother_mab.filter(completed=False)]

    try:
        discord = OnlineMedia.objects.get(name='Discord')
    except ObjectDoesNotExist:
        discord = None

    if request.method == 'POST':
        pk = request.POST.get('id')
        if brother.brother_status == '0':
            mabro = brother.candidate_mab.get(brother=pk)
            mabro.completed = True
            mabro.save()
        elif brother.brother_status == '1':
            mabro = brother.brother_mab.get(candidate=pk)
            mabro.completed = True
            mabro.save()
        return HttpResponseRedirect(reverse('dashboard:brother'))


    context = {
        'brother': brother,
        'chapter_attendance': chapter_attendance,
        'operational_committees': operational_committees,
        'standing_committees': standing_committees,
        'meetings': meetings,
        'hs_attendance': hs_attendance,
        'recruitment_events_next': recruitment_events_next,
        'recruitment_attendance': recruitment_attendance,
        'pnms': pnms,
        'service_attendance': service_attendance,
        'submissions_pending': submissions_pending,
        'submissions_submitted': submissions_submitted,
        'submissions_approved': submissions_approved,
        'submissions_denied': submissions_denied,
        'philanthropy_attendance': philanthropy_attendance,
        'hours_approved': hours_approved,
        'hours_pending': hours_pending,
        'type': 'brother-view',
        'notifies': notifies(brother),
        'notified_by': notified_by(brother),
        'mab': mab,
        'discord': discord,
    }
    return render(request, "brother.html", context)


def brother_chapter_event(request, event_id, view):
    """ Renders the brother page for chapter event with a excuse form """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother chapter events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    event = ChapterEvent.objects.get(pk=event_id)
    form = ExcuseForm(request.POST or None)

    brother = request.user.brother
    # get the excuses the brother has submitted for this event
    excuse = Excuse.objects.filter(event=event_id, brother=brother)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.brother = brother
            instance.event = event
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'type': view,
        'form': form,
        'event': event,
        'excuse_exists': excuse.exists(),
        'brother': brother,
        'attended': event.attendees_brothers.filter(pk=brother.pk).exists()
    }

    # if an excuse has been submitted, add the excuse to the context
    if excuse.exists():
        context.update({ 'excuse': excuse[0], })

    return render(request, "chapter-event.html", context)


def brother_service_event(request, event_id, view):
    """ Renders the brother page for service event with a excuse form """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother chapter events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brother = request.user.brother
    # get the excuses the brother has submitted for this event
    excuse = Excuse.objects.filter(event=event_id, brother=brother)
    event = ServiceEvent.objects.get(pk=event_id)
    rsvp_brother = event.rsvp_brothers.filter(id=brother.id)
    form = ExcuseForm(request.POST or None)

    if request.method == 'POST':
        if 'excuse' in request.POST:
            if form.is_valid():
                instance = form.save(commit=False)
                instance.brother = brother
                instance.event = event
                instance.save()
        if 'rsvp' in request.POST:
            event.rsvp_brothers.add(brother)
            event.save()
        if 'cancel_rsvp' in request.POST:
            event.rsvp_brothers.remove(brother)
            event.save()
        return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'type': view,
        'rsvpd': rsvp_brother.exists(),
        'event': event,
        'form': form,
        'excuse_exists': excuse.exists(),
        'attended': event.attendees_brothers.filter(pk=brother.pk).exists()
    }

    # if an excuse has been submitted, add the excuse to the context
    if excuse.exists():
        context.update({ 'excuse': excuse[0], })

    return render(request, "service-event.html", context)


def brother_philanthropy_event(request, event_id, view):
    """ Renders the brother page for service event with a excuse form """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother chapter events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brother = request.user.brother
    # get the excuses the brother has submitted for this event
    excuse = Excuse.objects.filter(event=event_id, brother=brother)
    event = PhilanthropyEvent.objects.get(pk=event_id)
    brothers_rsvp = event.rsvp_brothers.all()
    rsvp_brother = event.rsvp_brothers.filter(id=brother.id)

    form = ExcuseForm(request.POST or None)

    if request.method == 'POST':
        if 'excuse' in request.POST:
            if form.is_valid():
                instance = form.save(commit=False)
                instance.brother = brother
                instance.event = event
                instance.save()
        if 'rsvp' in request.POST:
            if rsvp_brother.exists():
                event.rsvp_brothers.remove(brother)
            else:
                event.rsvp_brothers.add(brother)
            event.save()
        return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'type': view,
        'brothers_rsvp': brothers_rsvp,
        'rsvpd': rsvp_brother.exists(),
        'event': event,
        'form': form,
        'excuse_exists': excuse.exists(),
        'attended': event.attendees_brothers.filter(pk=brother.pk).exists()
    }

    # if an excuse has been submitted, add the excuse to the context
    if excuse.exists():
        context.update({ 'excuse': excuse[0], })

    return render(request, "philanthropy-event.html", context)


def brother_recruitment_event(request, event_id, view):
    """ Renders the brother page for recruitment event with a excuse form """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother chapter events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brother = request.user.brother
    # get the excuses the brother has submitted for this event
    excuse = Excuse.objects.filter(event=event_id, brother=brother)

    event = RecruitmentEvent.objects.get(pk=event_id)
    attendees_pnms = event.attendees_pnms.all()

    form = ExcuseForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.brother = brother
            instance.event = event
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'form': form,
        'type': view,
        'attendees_pnms': attendees_pnms,
        'event': event,
        'excuse_exists': excuse.exists(),
        'attended': event.attendees_brothers.filter(pk=brother.pk).exists()
    }

    # if an excuse has been submitted, add the excuse to the context
    if excuse.exists():
        context.update({ 'excuse': excuse[0], })

    return render(request, "recruitment-event.html", context)


def brother_hs_event(request, event_id, view):
    """ Renders the brother page for health and safety event with a excuse form """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before viewing brother Health and Safety events")
        return HttpResponseRedirect(reverse('dashboard:home'))

    brother = request.user.brother
    # get the excuses the brother has submitted for this event
    excuse = Excuse.objects.filter(event=event_id, brother=brother)

    event = HealthAndSafetyEvent.objects.get(pk=event_id)

    form = ExcuseForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.brother = brother
            instance.event = event
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'type': view,
        'event': event,
        'form': form,
        'excuse_exists': excuse.exists(),
        'brother': brother,
        'attended': event.attendees_brothers.filter(pk=brother.pk).exists()
    }

    # if an excuse has been submitted, add the excuse to the context
    if excuse.exists():
        context.update({ 'excuse': excuse[0], })

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
    form_class = BrotherEditForm


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
    if not request.user.is_authenticated:  # brother auth check
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
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother not logged in before adding service hours")
        return HttpResponseRedirect(reverse('dashboard:home'))

    form = ServiceSubmissionForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            semester = get_semester()
            brother = request.user.brother
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
    form_class = ServiceSubmissionForm


def campus_groups_add(request):

    brother = request.user.brother

    form = CampusGroupForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            group, created = CampusGroup.objects.get_or_create(name=instance.name)
            group.brothers.add(brother)
            group.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'brother': brother,
        'title': 'Add Your Campus Groups',
        'form': form,
    }

    return render(request, 'model-add.html', context)


def campus_groups_delete(request, pk):
    brother = request.user.brother
    CampusGroup.objects.get(pk=pk).brothers.remove(brother)

    return HttpResponseRedirect(reverse('dashboard:brother'))


def media_account_add(request):

    brother = request.user.brother
    form = MediaAccountForm(request.POST or None)

    form.fields["media"].queryset = OnlineMedia.objects.exclude(name__in=[e.media.name for e in brother.media_accounts.all()])
    #list(map(lambda account: account.media.name, brother.media_accounts.all()))
    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            instance.brother = brother
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:brother'))

    context = {
        'brother': request.user.brother,
        'title': 'Media Account',
        'form': form,
        'list': brother.media_accounts.all()
    }

    return render(request, 'brother-info-add.html', context)


class MediaAccountDelete(DeleteView):
    def get(self, request, *args, **kwargs):
        return super(MediaAccountDelete, self).get(request, *args, **kwargs)

    model = MediaAccount
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:brother')


def media_add(request):

    form = MediaForm(request.POST or None)

    if request.method == 'POST':
        form = MediaForm(request.POST, request.FILES or None)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('dashboard:media_account_add'))

    context = {
        'title': 'Media',
        'form': form
    }

    return render(request, 'model-add.html', context)


@verify_position(['President', 'Adviser'])
def president(request):
    """ Renders the President page and all relevant information """
    return render(request, 'president.html', {'semester_picker': SelectSemester()})


@verify_position(['Vice President', 'President', 'Adviser'])
def vice_president(request):
    """ Renders the Vice President page and all relevant information, primarily committee related """
    committee_meetings = CommitteeMeetingEvent.objects.filter(semester=get_semester())\
        .order_by("start_time").order_by("date")
    committees = Committee.objects.all()

    context = {
        'position': 'Vice President',
        'committees': committees,
        'committee_meetings': committee_meetings,
    }

    return render(request, 'vice-president.html', context)


@verify_position(['Vice President', 'President', 'Adviser'])
def vice_president_committee_assignments(request):
    """Renders Committee assignment update page for the Vice President"""
    form_list = []
    brothers = Brother.objects.exclude(brother_status='2').order_by('last_name', 'first_name')
    for brother in brothers:
        new_form = CommitteeForm(request.POST or None,
                                 initial={'standing_committees': get_standing_committees(brother),
                                          'operational_committees': get_operational_committees(brother)},
                                 prefix=brother.id)
        form_list.append(new_form)

    brother_forms = zip(brothers, form_list)

    if request.method == 'POST':
        if forms_is_valid(form_list):
            meeting_map = {}
            for counter, form in enumerate(form_list):
                instance = form.cleaned_data
                # since the form was created in the same order that the brothers are ordered in you can just use
                # counter to get the brother associated with the form
                brother = brothers[counter]
                # all the committees the brother was a part of before new committees were assigned
                brother_committees = get_standing_committees(brother) + get_operational_committees(brother)
                # unassigns the brother from all of their committees
                brother.committee_set.clear()
                # list of the committees the brother was now assigned to as strings representing the committees
                chosen_committees = instance['standing_committees'] + instance['operational_committees']
                # all committee options
                committee_choices = [x for x,y in form.fields['standing_committees'].choices] + [x for x,y in form.fields['operational_committees'].choices]
                for committee in committee_choices:
                    # if the committee is one that the brother has been assigned to
                    if committee in chosen_committees:
                        # adds the brother to the committee's member list again
                        committee_object = Committee.objects.get(committee=committee)
                        committee_object.members.add(brother)
                        committee_object.save()
                        # if the brother was not previously a part of the committee
                        if committee not in brother_committees:
                            # iterates through all of the committee meetings after now
                            for meeting in committee_object.meetings.exclude(date__lte=datetime.datetime.now(), eligible_attendees=brother):
                                # if the meeting hasn't been previously added to the committee_map, adds it
                                # adds brother: true to the dictionary associated with this meeting
                                if meeting not in meeting_map:
                                    meeting_map[meeting] = {brother: True}
                                # if the meeting has been added, add the brother to the dictionary
                                else:
                                    meeting_map[meeting][brother] = True
                    # if the brother wasn't added to this committee
                    else:
                        # if the the brother was previously part of this commitee
                        if committee in brother_committees:
                            # iterate through all of the committee meetings after now
                            for meeting in Committee.objects.get(committee=committee).meetings.filter(date__gt=datetime.datetime.now(), eligible_attendees=brother):
                                # same as above but false instead of true is assigned to the brother
                                if meeting not in meeting_map:
                                    meeting_map[meeting] = {brother: False}
                                else:
                                    meeting_map[meeting][brother] = False
            # for every meeting in the mapping, add the brothers associated with that meeting to the
            # eligible attendees list if true is assigned to the brother, and removes it if false
            for meeting, brother_map in meeting_map.items():
                add_list = [brother_face for brother_face, boo in brother_map.items() if boo is True]
                remove_list = [brother_face for brother_face, boo in brother_map.items() if boo is False]
                meeting.eligible_attendees.add(*add_list)
                meeting.eligible_attendees.remove(*remove_list)
                meeting.save()
            return HttpResponseRedirect(reverse('dashboard:committee_list'))
    context = {
        'brother_forms': brother_forms,
    }

    return render(request, 'committee-assignment.html', context)


def committee_list(request):
    committees = Committee.objects.all()
    brothers = Brother.objects.order_by('last_name')
    current_brother = request.user.brother
    form = CommitteeCreateForm(request.POST or None)
    form.fields["committee"].choices = [e for e in form.fields["committee"].choices if not Committee.objects.filter(committee=e[0]).exists()]
    form.fields["chair"].choices = [e for e in form.fields["chair"].choices if e[0] not in Committee.objects.values_list('chair', flat=True)]

    if current_brother.position_set.filter(title='Vice President'):
        view_type = 'Vice President'
    else:
        view_type = 'brother'

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            instance = form.cleaned_data
            create_recurring_meetings(instance, instance['committee'])
            return HttpResponseRedirect(reverse('dashboard:committee_list'))

    context = {
        'committees': committees,
        'brothers': brothers,
        'form': form,
        'view_type': view_type
    }

    return render(request, 'committee-list.html', context)


class CommitteeDelete(DeleteView):
    @verify_position(['Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(CommitteeDelete, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return HttpResponseRedirect(reverse('dashboard:committee_list'))

    model = Committee
    template_name = 'dashboard/base_confirm_delete.html'


class CommitteeEdit(UpdateView):
    def get(self, request, *args, **kwargs):
        return super(CommitteeEdit, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.GET.get('next')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('committee')
        return context

    def form_valid(self, form):
        self.object.meetings.filter(recurring=True).exclude(date__lt=datetime.date.today()+datetime.timedelta(days=1)).delete()
        committee = self.object.committee
        form.save()
        instance = form.cleaned_data
        create_recurring_meetings(instance, committee)
        return super().form_valid(form)

    model = Committee
    fields = ['meeting_day', 'meeting_time', 'meeting_interval']


def committee_event(request, event_id):
    event = CommitteeMeetingEvent.objects.get(pk=event_id)

    brothers = event.eligible_attendees.all()
    brother_form_list = []
    current_brother = request.user.brother

    if current_brother in event.committee.chair.brothers.all():
        view_type = 'chairman'
    else:
        view_type = 'brother'

    for counter, brother in enumerate(brothers):
        new_form = BrotherAttendanceForm(request.POST or None, initial={'present':  event.attendees_brothers.filter(id=brother.id).exists()},
                                         prefix=counter,
                                         brother="- %s %s" % (brother.first_name, brother.last_name))
        brother_form_list.append(new_form)

    form = EditBrotherAttendanceForm(request.POST or None, event=event_id)

    if request.method == 'POST':
        if "update" in request.POST:
            if forms_is_valid(brother_form_list):
                mark_attendance_list(brother_form_list, brothers, event)
        if "edit" in request.POST:
            if form.is_valid():
                instance = form.cleaned_data
                update_eligible_brothers(instance, event)
        return redirect(request.path_info, kwargs={'event_id': event_id})

    context = {
        'type': view_type,
        'brother_form_list': brother_form_list,
        'event': event,
        'form': form,
    }

    return render(request, "committee_event.html", context)


@verify_position(['Public Relations Chair', 'Scholarship Chair', 'Service Chair', 'Philanthropy Chair', 'Alumni Relations Chair', 'Membership Development Chair', 'Social Chair', 'Vice President of Health and Safety', ' Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def committee_event_add(request, position):
    """ Renders the committee meeting add page """
    form = CommitteeMeetingForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            committee = Position.objects.get(title=position).committee
            eligible_attendees(committee.members.order_by('last_name'))
            instance.committee = committee
            save_event(instance, eligible_attendees)
            next = request.GET.get('next')
            return HttpResponseRedirect(next)

    context = {
        'title': 'Committee Meeting',
        'form': form,
        'position': position
    }
    return render(request, 'event-add.html', context)


class CommitteeEventDelete(DeleteView):
    @verify_position(['Recruitment Chair', 'Vice President of Health and Safety', 'Scholarship Chair', 'Philanthropy Chair', 'Alumni Relations Chair', 'Public Relations Chair', 'Membership Development Chair', 'Social Chair', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(CommitteeEventDelete, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.GET.get('next')

    model = CommitteeMeetingEvent
    template_name = 'dashboard/base_confirm_delete.html'


class CommitteeEventEdit(UpdateView):
    @verify_position(['Recruitment Chair', 'Vice President of Health and Safety', 'Scholarship Chair', 'Philanthropy Chair', 'Alumni Relations Chair', 'Public Relations Chair', 'Membership Development Chair', 'Social Chair', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(CommitteeEventEdit, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('dashboard:committee_event', args=[int(self.request.GET.get('id'))])

    model = CommitteeMeetingEvent
    form_class = CommitteeMeetingForm


@verify_position(['President', 'Adviser', 'Vice President', 'Vice President of Health and Safety'])
def vphs(request):
    """ Renders the VPHS and the events they can create """
    events = HealthAndSafetyEvent.objects.filter(semester=get_semester()).order_by("start_time").order_by("date")
    committee_meetings, context = committee_meeting_panel('Vice President of Health and Safety')

    context.update({
        'position': 'Vice President of Health and Safety',
        'events': events,
    })
    return render(request, 'vphs.html', context)


@verify_position(['President', 'Adviser', 'Vice President', 'Vice President of Health and Safety'])
def health_and_safety_event_add(request):
    """ Renders the VPHS adding an event """
    form = HealthAndSafetyEventForm(request.POST or None, initial={'name': 'Sacred Purpose Event'})

    if form.is_valid():
        # TODO: add google calendar event adding
        instance = form.save(commit=False)
        eligible_attendees = Brother.objects.exclude(brother_status='2').order_by('last_name')
        save_event(instance, eligible_attendees)
        return HttpResponseRedirect(reverse('dashboard:vphs'))

    context = {
        'title': 'Add New Health and Safety Event',
        'form': form,
    }
    return render(request, 'model-add.html', context)


class HealthAndSafetyEdit(UpdateView):
    @verify_position(['President', 'Adviser', 'Vice President', 'Vice President of Health and Safety'])
    def get(self, request, *args, **kwargs):
        return super(HealthAndSafetyEdit, self).get(request, *args, **kwargs)

    model = HealthAndSafetyEvent
    success_url = reverse_lazy('dashboard:vphs')
    form_class = HealthAndSafetyEventForm


class HealthAndSafetyDelete(DeleteView):
    @verify_position(['President', 'Adviser', 'Vice President', 'Vice President of Health and Safety'])
    def get(self, request, *args, **kwargs):
        return super(HealthAndSafetyDelete, self).get(request, *args, **kwargs)

    model = HealthAndSafetyEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:vphs')


def health_and_safety_event(request, event_id):
    """ Renders the vphs way of view events """
    event = Event.objects.get(pk=event_id)
    brothers, brother_form_list = attendance_list(request, event)

    form = EditBrotherAttendanceForm(request.POST or None, event=event_id)

    if request.method == 'POST':
        if "update" in request.POST:
            if forms_is_valid(brother_form_list):
                mark_attendance_list(brother_form_list, brothers, event)
        if "edit" in request.POST:
            if form.is_valid():
                instance = form.cleaned_data
                update_eligible_brothers(instance, event)
        return redirect(request.path_info, kwargs={'event_id': event_id})

    context = {
        'type': 'attendance',
        'brother_form_list': brother_form_list,
        'event': event,
        'form': form,
    }
    return render(request, "hs-event.html", context)


@verify_position(['Treasurer', 'President', 'Adviser'])
def treasurer(request):
    """ Renders all the transactional information on the site for the treasurer """
    return render(request, 'treasurer.html', {})


def cleaned_brother_data(line):
    stripped_data = [data.strip() for data in line.strip().split(",")]

    for i in range(len(stripped_data), 3):
        stripped_data.append("")

    return stripped_data[0:3]


def can_brother_be_added(first_name, last_name, caseid):
    data = [first_name, last_name, caseid]

    return all(value != "" for value in data) and not Brother.objects.filter(case_ID=caseid).exists()


def create_brother_if_possible(semester, brother_status, first_name, last_name, caseid):
    if User.objects.filter(username=caseid).exists():
        user = User.objects.get(username=caseid)
    elif caseid != "":
        user = User()
        user.username = caseid
        user.save()
    else:
        pass  # nothing to do here since the if below will return false
                # ie `user` is never accessed

    # if able to add, create the brother with the given data
    if can_brother_be_added(first_name, last_name, caseid):
        new_brother = Brother()
        new_brother.user = user
        new_brother.first_name = first_name
        new_brother.last_name = last_name
        new_brother.case_ID = user.username
        new_brother.birthday = datetime.date.today()
        new_brother.semester = semester
        new_brother.brother_status = brother_status
        new_brother.save()


def create_mass_entry_brothers(request, mass_entry_form):
    if mass_entry_form.is_valid():
        data = mass_entry_form.cleaned_data
        brother_data = data["brothers"].split("\n")
        semester = data["semester"]
        brother_status = data["brother_status"]

        for brother in brother_data:
            create_brother_if_possible(semester, brother_status, *cleaned_brother_data(brother))

    else:
        messages.error(request, "Mass entry form invalid")


def staged_mass_entry_brothers(mass_entry_form):
    brothers = []
    mass_entry_form.fields['brothers'].widget.attrs['readonly'] = True
    if mass_entry_form.is_valid():
        data = mass_entry_form.cleaned_data
        brother_data = data["brothers"].split("\n")

        for brother in brother_data:

            first, last, caseid = cleaned_brother_data(brother)

            brothers.append({
                'first_name': first,
                'last_name': last,
                'caseid': caseid,
                'will_be_added': can_brother_be_added(first, last, caseid)
            })

    return brothers


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary(request):
    """ Renders the secretary page giving access to excuses and ChapterEvents """
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='0').exclude(event__in=RecruitmentEvent.objects.all()).order_by("date_submitted", "event__date")
    events = ChapterEvent.objects.filter(semester=get_semester()).order_by("start_time").order_by("date")
    brothers = []

    if request.method == 'POST':
        mass_entry_form = BrotherMassEntryForm(request.POST)
        mass_entry_form.fields['brothers'].widget.attrs['readonly'] = False
        is_entry = False

        if "confirmation" in request.POST:
            create_mass_entry_brothers(request, mass_entry_form)
            return HttpResponseRedirect(reverse('dashboard:home'))

        elif "goback" in request.POST:
            is_entry = True  # just want to go back to adding/editting data

        # however else we got here, we need to show the staged data
        else:
            brothers = staged_mass_entry_brothers(mass_entry_form)
    else:
        mass_entry_form = BrotherMassEntryForm()
        is_entry = True

    context = {
        'excuses': excuses,
        'events': events,
        'mass_entry_form': mass_entry_form,
        'is_entry': is_entry, # TODO change to have post stuff
        'brothers': brothers,
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
    event = Event.objects.get(pk=event_id)
    brothers, brother_form_list = attendance_list(request, event)

    form = EditBrotherAttendanceForm(request.POST or None, event=event_id)

    if request.method == 'POST':
        if "update" in request.POST:
            if forms_is_valid(brother_form_list):
                mark_attendance_list(brother_form_list, brothers, event)
        if "edit" in request.POST:
            if form.is_valid():
                instance = form.cleaned_data
                update_eligible_brothers(instance, event)
        return redirect(request.path_info, kwargs={'event_id': event_id})

    context = {
        'type': 'attendance',
        'brother_form_list': brother_form_list,
        'event': event,
        'form': form,
    }
    return render(request, "chapter-event.html", context)


@verify_position(['Recruitment Chair', 'Secretary', 'Vice President', 'President', 'Adviser'])
def excuse(request, excuse_id):
    """ Renders Excuse response form """
    excuse = get_object_or_404(Excuse, pk=excuse_id)
    form = ExcuseResponseForm(request.POST or None, excuse=excuse)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            excuse.status = instance.status
            excuse.response_message = instance.response_message
            excuse.save()
            return HttpResponseRedirect(request.GET.get('next'))

    context = {
        'type': 'response',
        'excuse': excuse,
        'form': form,
    }
    return render(request, "excuse.html", context)


# accepts the excuse then immediately redirects you back to where you came from
def excuse_quick_accept(request, excuse_id):
    excuse = Excuse.objects.get(pk=excuse_id)
    excuse.status = '1'
    excuse.save()
    return HttpResponseRedirect(request.GET.get('next'))


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_all_excuses(request):
    """ Renders Excuse archive """
    excuses = Excuse.objects.exclude(status='0').exclude(event__in=RecruitmentEvent.objects.all()).order_by('brother__last_name', 'event__date')

    context = {
        'excuses': excuses,
        'position': 'Secretary',
    }
    return render(request, 'excuses_archive.html', context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_event_view(request, event_id):
    """ Renders the Secretary way of viewing old events """
    event = ChapterEvent.objects.get(pk=event_id)
    attendees = event.attendees_brothers.all().order_by("last_name", "first_name")

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
        'brother': brother,
        'position': 'Secretary'
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
    form_class = BrotherEditForm


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
    form = ChapterEventForm(request.POST or None, initial={'name': 'Chapter Event'})

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            save_event(instance)
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
    form_class = ChapterEventForm


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
    if request.method == 'POST':
        for position in all_positions:
            if not Position.objects.filter(title=position).exists():
                new_position = Position(title=position)
                new_position.save()
        return HttpResponseRedirect(reverse('dashboard:secretary_positions'))

    positions = Position.objects.order_by("title")
    context = {
        'positions': positions,
    }
    return render(request, "positions.html", context)


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_position_add(request):
    """ Renders the Secretary way of viewing a brother """
    form = PositionForm(request.POST or None)
    form.fields["title"].choices = [e for e in form.fields["title"].choices if not Position.objects.filter(title=e[0]).exists()]

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
    fields = ['brothers']


class PositionDelete(DeleteView):
    @verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PositionDelete, self).get(request, *args, **kwargs)

    model = Position
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:secretary_positions')


@verify_position(['Secretary', 'Vice President', 'President', 'Adviser'])
def secretary_agenda(request):
    c_reports = Report.objects.filter(is_officer=False).order_by('brother')
    communications = []
    previous = Brother
    brother = []
    for communication in c_reports:
        if previous == communication.brother:
            brother.append(communication)
        else:
            if brother:
                communications.append(brother)
            brother = [communication]
            previous = communication.brother
    communications.append(brother)

    o_reports = Report.objects.filter(is_officer=True).order_by('position')
    reports = []
    previous = Position
    position = []
    for report in o_reports:
        if previous == report.position:
            position.append(report)
        else:
            if position:
                reports.append(position)
            position = [report]
            previous = report.position
    reports.append(position)

    if request.method == 'POST':
        Report.objects.all().delete()
        return HttpResponseRedirect(reverse('dashboard:secretary_agenda'))

    context = {
        'communications': communications,
        'reports': reports,
    }

    return render(request, 'secretary-agenda.html', context)



@verify_position(['Marshal', 'Vice President', 'President', 'Adviser'])
def marshal(request):
    """ Renders the marshal page listing all the candidates and relevant information to them """
    candidates = Brother.objects.filter(brother_status='0').order_by("last_name", "first_name")
    events = ChapterEvent.objects.filter(semester=get_semester()).exclude(date__gt=datetime.date.today())
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='1')
    events_excused_list = []
    events_unexcused_list = []
    randomized_list = request.session.pop('randomized_list', None)

    mab_form_list = []

    for counter, candidate in enumerate(candidates):
        assigned_mab = MeetABrother.objects.filter(candidate=candidate).values_list('brother', flat=True)
        eligible_brothers = Brother.objects.filter(brother_status=1).exclude(pk__in=assigned_mab).order_by('last_name', 'first_name')
        form = MeetABrotherForm(request.POST or None, prefix=counter+1, candidate=candidate.first_name + ' ' + candidate.last_name)
        mab_form_list.append(form)
        if randomized_list is not None or []:
            form.fields['assigned_brother1'].initial = randomized_list[counter][0]
            form.fields['assigned_brother2'].initial = randomized_list[counter][1]
            form.fields['randomize'].initial = randomized_list[counter][2]
        else:
            form.fields['randomize'].initial = True
        form.fields['assigned_brother1'].queryset = eligible_brothers
        form.fields['assigned_brother2'].queryset = eligible_brothers

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

    if request.method == 'POST':
        if 'submit' in request.POST:
            if forms_is_valid(mab_form_list):
                for counter, form in enumerate(mab_form_list):
                    instance = form.cleaned_data
                    if instance['assigned_brother1']:
                        mab1 = MeetABrother(candidate=candidates[counter], brother=instance['assigned_brother1'])
                        mab1.save()
                    if instance['assigned_brother2']:
                        mab2 = MeetABrother(candidate=candidates[counter], brother=instance['assigned_brother2'])
                        mab2.save()
                return HttpResponseRedirect(reverse('dashboard:meet_a_brother'))
        if 'randomize' in request.POST:
            if forms_is_valid(mab_form_list):
                randomized_list = []
                random1 = []
                random2 = []
                for form in mab_form_list:
                    instance = form.cleaned_data
                    if instance['randomize']:
                        queryset1 = form.fields['assigned_brother1'].queryset
                        queryset2 = queryset1
                        if queryset1.exists():
                            random1 = random.choices(queryset1, k=1)[0].pk
                            queryset2 = queryset1.exclude(pk=random1)
                        if queryset2.exists():
                            random2 = random.choices(queryset2, k=1)[0].pk
                        randomized_list.append((random1, random2, True))
                    else:
                        if instance['assigned_brother1']:
                            random1 = instance['assigned_brother1'].pk
                        else:
                            random1 = []
                        if instance['assigned_brother2']:
                            random2 = instance['assigned_brother2'].pk
                        else:
                            random2 = []
                        randomized_list.append((random1, random2, instance['randomize']))
                request.session['randomized_list'] = randomized_list
                return HttpResponseRedirect(reverse('dashboard:marshal'))

    context = {
        'candidates': candidates,
        'candidate_attendance': candidate_attendance,
        'mab_form_list': mab_form_list,
    }
    return render(request, 'marshal.html', context)


def marshal_mab_edit_candidate(request):
    initial = {'candidate': request.session.pop('candidate', None)}
    form = MABEditCandidateForm(request.POST or None, initial=initial)

    if request.method == 'POST':
        if form.is_valid():
            request.session['candidate'] = form.cleaned_data['candidate'].pk
            return HttpResponseRedirect(reverse('dashboard:marshal_mab_edit'))

    context = {
        'form': form,
    }

    return render(request, 'marshal-mab-edit-candidate.html', context)


def marshal_mab_edit(request):
    candidate = Brother.objects.get(pk=request.session.get('candidate', None))
    check_all = request.session.pop('check_all', False)

    mab_form_list = []

    brothers = Brother.objects.filter(brother_status='1')


    arbitrary_date_before_time = datetime.datetime(1000, 1, 1)

    for counter, brother in enumerate(brothers):
        form = MeetABrotherEditForm(request.POST or None, prefix=counter+1, brother=brother.pk, mab_exists=MeetABrother.objects.filter(brother=brother, candidate=candidate).exists())
        if check_all:
            form.fields['update'].initial = True
        mab_form_list.append(form)

    if request.method == 'POST':
        if 'submit' in request.POST:
            if forms_is_valid(mab_form_list):
                for counter, form in enumerate(mab_form_list):
                    instance = form.cleaned_data
                    if instance['update'] is True: #the user checked yes on this pairing of meet a brother, meaning we need to create a new one if it doesn't yet exist
                        mab, created = MeetABrother.objects.get_or_create(candidate=candidate, brother=brothers[counter], defaults={'completed':True, 'week':arbitrary_date_before_time})
                        if created: #if a new meet a brother is created we need to save it
                            mab.save()
                    elif instance['update'] is False: #the user has not checked yes on this pairing of meet a brother
                        # we need to delete this meet a brother if it exists
                        try: #get the meet a brother and delete it if it finds it
                            MeetABrother.objects.get(candidate=candidate, brother=brothers[counter]).delete()
                        except MeetABrother.DoesNotExist: #get will return this exception if it doesn't find one so just continue if it's not found
                            continue
                    else:
                        pass # instance['update'] is null
        if 'check_all' in request.POST:
            request.session['check_all'] = True
            return HttpResponseRedirect(reverse('dashboard:marshal_mab_edit'))
        if 'go_back' in request.POST:
            return HttpResponseRedirect(reverse('dashboard:marshal_mab_edit_candidate'))

    context = {
        'candidate': candidate,
        'mab_form_list': mab_form_list,
    }

    return render(request, 'marshal-mab-edit.html', context)


def meet_a_brother(request):
    start_date = datetime.datetime(2000, 1, 1)
    candidates = Brother.objects.filter(brother_status=0)

    weeks = MeetABrother.objects.filter(week__range=(start_date, datetime.datetime.now())).order_by('-week').values_list('week', flat=True).distinct
    try:
        discord = OnlineMedia.objects.get(name='Discord')
    except ObjectDoesNotExist:
        discord = None

    context = {
        'candidates': candidates,
        'weeks': weeks,
        'discord': discord,
    }

    return render(request, 'meet-a-brother.html', context)


@verify_position(['Marshal', 'Vice President', 'President', 'Adviser'])
def marshal_candidate(request, brother_id):
    """ Renders the marshal page to view candidate info """
    brother = Brother.objects.get(pk=brother_id)
    context = {
        'brother': brother,
        'position': 'Marshal',
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
    form_class = CandidateEditForm


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

    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name", "first_name")
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

    committee_meetings, context = committee_meeting_panel('Scholarship Chair')

    context.update({
        'position': 'Scholarship Chair',
        'events': events,
        'brother_plans': brother_plans,
    })
    return render(request, "scholarship-chair.html", context)


@verify_position(['Scholarship Chair', 'President', 'Adviser'])
def study_table_event(request, event_id):
    """ Renders the scholarship chair way of view StudyTables """
    event = StudyTableEvent.objects.get(pk=event_id)
    brothers, brother_form_list = attendance_list(request, event)

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
    form = StudyTableEventForm(request.POST or None, initial={'name': 'Scholarship Event'})

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            semester, _ = Semester.objects.get_or_create(season=get_season_from(instance.date.month),
                   year=instance.date.year)
            instance.semester = semester
            instance.save()
            instance.eligible_attendees.set(Brother.objects.exclude(brother_status='2').order_by('last_name'))
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
    form_class = StudyTableEventForm


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
    """ Renders Recruitment chair page with events for the current and following semester """
    events = RecruitmentEvent.objects.all()
    excuses = Excuse.objects.filter(event__semester=get_semester(), status='0',
        event__in=events).order_by("date_submitted", "event__date")
    current_season = get_season()
    if current_season == '0':
        semester_events = RecruitmentEvent.objects.filter(semester__season='0', semester__year=get_year())
        semester_events_next = RecruitmentEvent.objects.filter(semester__season='2', semester__year=get_year())
    else:
        semester_events = RecruitmentEvent.objects.filter(semester__season='2', semester__year=get_year())
        semester_events_next = RecruitmentEvent.objects.filter(semester__season='0', semester__year=get_year())

    potential_new_members = PotentialNewMember.objects.all()

    committee_meetings, context = committee_meeting_panel('Recruitment Chair')

    context.update({
        'position': 'Recruitment Chair',
        'events': semester_events,
        'events_future': semester_events_next,
        'potential_new_members': potential_new_members,
        'excuses': excuses,
    })
    return render(request, 'recruitment-chair.html', context)


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_all_excuses(request):
    """ Renders Excuse archive"""
    excuses = Excuse.objects.exclude(status='0').filter(event__in=RecruitmentEvent.objects.all()).order_by('brother__last_name', 'event__date')

    context = {
        'excuses': excuses,
        'position': 'Recruitment Chair',
    }
    return render(request, 'excuses_archive.html', context)


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
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name", "first_name")
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
    form_class = PotentialNewMemberForm


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_event(request, event_id):
    """ Renders the recruitment chair way of view RecruitmentEvents """
    event = RecruitmentEvent.objects.get(pk=event_id)
    pnms = PotentialNewMember.objects.all().order_by('last_name')
    pnm_form_list = []
    brothers, brother_form_list = attendance_list(request, event)

    num_actives = len(brothers)

    form = EditBrotherAttendanceForm(request.POST or None, event=event_id)

    for counter, pnm in enumerate(pnms):
        new_form = PnmAttendanceForm(request.POST or None, initial={'present': event.attendees_pnms.filter(pk=pnm.id).exists()},
                                     prefix=num_actives + counter,
                                     pnm="- %s %s" % (pnm.first_name, pnm.last_name))
        pnm_form_list.append(new_form)

    if request.method == 'POST':
        if "updatebrother" in request.POST:
            if forms_is_valid(brother_form_list):
                mark_attendance_list(brother_form_list, brothers, event)
        if "updatepnm" in request.POST:
            if forms_is_valid(pnm_form_list):
                mark_attendance_list(pnm_form_list, pnms, event)
        if "edit" in request.POST:
            if form.is_valid():
                instance = form.cleaned_data
                update_eligible_brothers(instance, event)
        return redirect(request.path_info, kwargs={'event_id': event_id})

    context = {
        'type': 'attendance',
        'pnm_form_list': pnm_form_list,
        'brother_form_list': brother_form_list,
        'event': event,
        'media_root': settings.MEDIA_ROOT,
        'media_url': settings.MEDIA_URL,
        'form': form,
    }
    return render(request, "recruitment-event.html", context)


@verify_position(['Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def recruitment_c_event_add(request):
    """ Renders the recruitment chair way of adding RecruitmentEvents """
    form = RecruitmentEventForm(request.POST or None, initial={'name': 'Recruitment Event'})
    if request.method == 'POST':
        form = RecruitmentEventForm(request.POST, request.FILES or None)
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            semester, _ = Semester.objects.get_or_create(season=get_season_from(instance.date.month),
               year=instance.date.year)
            instance.semester = semester
            instance.save()
            instance.eligible_attendees.set(Brother.objects.exclude(brother_status='2').order_by('last_name'))
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

    form_class = RecruitmentEventForm
    model = RecruitmentEvent
    success_url = reverse_lazy('dashboard:recruitment_c')


@verify_position(['Service Chair', 'Adviser'])
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


@verify_position(['Service Chair', 'Adviser'])
def service_c_event(request, event_id):
    """ Renders the service chair way of adding ServiceEvent """
    event = Event.objects.get(pk=event_id)
    brothers, brother_form_list = attendance_list(request, event)

    form = EditBrotherAttendanceForm(request.POST or None, event=event_id)

    if request.method == 'POST':
        if "update" in request.POST:
            mark_attendance_list(brother_form_list, brothers, event)
        if "edit" in request.POST:
            if form.is_valid():
                instance = form.cleaned_data
                update_eligible_brothers(instance, event)
        return redirect(request.path_info, kwargs={'event_id': event_id})

    context = {
        'type': 'attendance',
        'brother_form_list': brother_form_list,
        'event': event,
        'form': form,
    }

    return render(request, 'service-event.html', context)


class ServiceEventDelete(DeleteView):
    @verify_position(['Service Chair', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ServiceEventDelete, self).get(request, *args, **kwargs)

    model = ServiceEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:service_c')


class ServiceEventEdit(UpdateView):
    @verify_position(['Service Chair', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(ServiceEventEdit, self).get(request, *args, **kwargs)

    model = ServiceEvent
    success_url = reverse_lazy('dashboard:service_c')
    form_class = ServiceEventForm


@verify_position(['Service Chair', 'Adviser'])
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


@verify_position(['Service Chair', 'Adviser'])
def service_c_event_add(request):
    """ Renders the service chair way of adding ServiceEvent """
    form = ServiceEventForm(request.POST or None, initial={'name': 'Service Event'})

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            semester, _ = Semester.objects.get_or_create(season=get_season_from(instance.date.month),
                   year=instance.date.year)
            instance.semester = semester
            instance.save()
            instance.eligible_attendees.set(Brother.objects.exclude(brother_status='2').order_by('last_name'))
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:service_c'))

    context = {
        'position': 'Service Chair',
        'form': form,
    }

    return render(request, 'event-add.html', context)


@verify_position(['Service Chair', 'Adviser'])
def service_c_hours(request):
    """ Renders the service chair way of viewing total service hours by brothers """
    brothers = Brother.objects.exclude(brother_status='2').order_by("last_name", "first_name")
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


@verify_position(['Philanthropy Chair', 'Adviser'])
def philanthropy_c(request):
    """ Renders the philanthropy chair's RSVP page for different events """
    events = PhilanthropyEvent.objects.filter(semester=get_semester())
    committee_meetings, context = committee_meeting_panel('Philanthropy Chair')

    context.update({
        'position': 'Philanthropy Chair',
        'events': events,
    })

    return render(request, 'philanthropy-chair.html', context)


@verify_position(['Philanthropy Chair', 'Adviser'])
def philanthropy_c_event(request, event_id):
    """ Renders the philanthropy event view """
    event = PhilanthropyEvent.objects.get(pk=event_id)
    brothers_rsvp = event.rsvp_brothers.all()
    brothers, brother_form_list = attendance_list(request, event)

    form = EditBrotherAttendanceForm(request.POST or None, event=event_id)

    if request.method == 'POST':
        if "update" in request.POST:
            if forms_is_valid(brother_form_list):
                mark_attendance_list(brother_form_list, brothers, event)
        if "edit" in request.POST:
            if form.is_valid():
                instance = form.cleaned_data
                update_eligible_brothers(instance, event)
        return redirect(request.path_info, kwargs={'event_id': event_id})

    context = {
        'type': 'attendance',
        'brother_form_list': brother_form_list,
        'brothers_rsvp': brothers_rsvp,
        'event': event,
        'form': form,
    }

    return render(request, 'philanthropy-event.html', context)


@verify_position(['Philanthropy Chair', 'Adviser'])
def philanthropy_c_event_add(request):
    """ Renders the philanthropy chair way of adding PhilanthropyEvent """
    form = PhilanthropyEventForm(request.POST or None, initial={'name': 'Philanthropy Event'})

    if request.method == 'POST':
        if form.is_valid():
            # TODO: add google calendar event adding
            instance = form.save(commit=False)
            semester, _ = Semester.objects.get_or_create(season=get_season_from(instance.date.month),
                   year=instance.date.year)
            instance.semester = semester
            instance.save()
            instance.eligible_attendees.set(Brother.objects.exclude(brother_status='2').order_by('last_name'))
            instance.save()
            return HttpResponseRedirect(reverse('dashboard:philanthropy_c'))

    context = {
        'position': 'Philanthropy Chair',
        'form': form,
    }
    return render(request, 'event-add.html', context)


class PhilanthropyEventDelete(DeleteView):
    @verify_position(['Philanthropy Chair', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PhilanthropyEventDelete, self).get(request, *args, **kwargs)

    model = PhilanthropyEvent
    template_name = 'dashboard/base_confirm_delete.html'
    success_url = reverse_lazy('dashboard:philanthropy_c')


class PhilanthropyEventEdit(UpdateView):
    @verify_position(['Philanthropy Chair', 'Adviser'])
    def get(self, request, *args, **kwargs):
        return super(PhilanthropyEventEdit, self).get(request, *args, **kwargs)

    model = PhilanthropyEvent
    success_url = reverse_lazy('dashboard:philanthropy_c')
    form_class = PhilanthropyEventForm


@verify_position(['Detail Manager', 'Adviser'])
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


@verify_position(['Detail Manager', 'Adviser'])
def supplies_finish(request):
    form = SuppliesFinishForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            for supply in form.cleaned_data['choices']:
                supply.done = True
                supply.save()

    context = {'form': form}
    return render(request, 'finish-supplies.html', context)


@verify_position(['Vice President', 'President', 'Adviser'])
@transaction.atomic
def in_house(request):
    """Allows the VP to select who's living in the house"""

    form = InHouseForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            InHouseForm.brothers.update(in_house=False)
            for c in ['in_house']:
                brothers = form.cleaned_data[c]
                for b in brothers:
                    b.in_house = True
                    b.save()
        return HttpResponseRedirect(reverse('dashboard:vice_president_in_house'))

    context = {'form': form}
    return render(request, 'in_house.html', context)


@verify_position(['Detail Manager', 'Adviser'])
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


@verify_position(['Detail Manager', 'Adviser'])
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


@verify_position(['Detail Manager', 'Adviser'])
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


@verify_position(['Detail Manager', 'Adviser'])
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


@verify_position(['Detail Manager', 'Adviser'])
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


@verify_position(['Detail Manager', 'Adviser'])
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


@verify_position(['Detail Manager', 'Adviser'])
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


@verify_position(['Detail Manager', 'Adviser'])
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


@verify_position(['Detail Manager', 'Adviser'])
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


@verify_position(['Detail Manager', 'Adviser'])
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


@verify_position(['Detail Manager', 'Adviser'])
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


@verify_position(['Detail Manager', 'Adviser'])
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


#@verify_position(['Public Relations Chair', 'Recruitment Chair', 'Vice President', 'President', 'Adviser'])
def public_relations_c(request):
    committee_meetings, context = committee_meeting_panel('Public Relations Chair')
    context.update({
        'form': photo_form(PhotoForm, request),
    })

    return render(request, 'public-relations-chair.html', context)


@verify_position(['Social Chair', 'Vice President', 'President', 'Adviser'])
def social_c(request):
    committee_meetings, context = committee_meeting_panel('Social Chair')

    return render(request, 'social-chair.html', context)


@verify_position(['Membership Development Chair', 'Vice President', 'President', 'Adviser'])
def memdev_c(request):
    committee_meetings, context = committee_meeting_panel('Membership Development Chair')

    return render(request, 'memdev-chair.html', context)


@verify_position(['Alumni Relations Chair', 'Vice President', 'President', 'Adviser'])
def alumni_relations_c(request):
    committee_meetings, context = committee_meeting_panel('Alumni Relations Chair')

    return render(request, 'alumni-relations-chair.html', context)


def minecraft(request):
    return render(request, 'minecraft.html', photo_context(MinecraftPhoto))


def emergency_phone_tree_view(request):
    """ Renders the brother page of current user showing all standard brother information """
    if not request.user.is_authenticated:  # brother auth check
        messages.error(request, "Brother needs to be logged in before viewing brother portal")
        return HttpResponseRedirect(reverse('dashboard:home'))

    ec_positions = filter(Position.in_ec, Position.objects.all())

    phone_tree = []
    for position in ec_positions:
        brother = position.brothers.all()[0]
        phone_tree.append({
            'position': position,
            'brother': brother,
            'notifies': notifies(brother)
        })

    context = {
        'phone_tree' : phone_tree
    }

    return render(request, 'emergency_phone_tree.html', context)

@verify_position(['President', 'Adviser'])
def create_phone_tree(request):
    """Creates the new phone tree and redirects to to the phone tree view."""
    # delete the exiting phone tree
    PhoneTreeNode.objects.all().delete()

    # Should only ever have 1 of each EC position
    president = Position.objects.filter(title='President')[0].brothers.all()[0]
    marshal = Position.objects.filter(title='Marshal')[0].brothers.all()[0]

    # get all the EC brothers that are not the president nor marshal
    standard_ec_brothers = list(
        map(lambda pos : pos.brothers.all()[0],
            filter(Position.in_ec, Position.objects.exclude(title='President') \
                                                   .exclude(title='Marshal'))))

    all_ec_brothers = standard_ec_brothers + [president, marshal]

    actives = Brother.objects.filter(brother_status='1') \
                             .exclude(user__in=list(map(lambda bro : bro.user, all_ec_brothers)))

    candidates = Brother.objects.filter(brother_status='0')

    # president's child nodes are implicitly created by the node creation functions below
    PhoneTreeNode(brother=president).save()

    create_node_with_children(marshal, president, candidates)

    actives_index = 0
    num_non_ec = len(actives)
    num_standard_ec = len(standard_ec_brothers)
    actives_per_ec_member = int(num_non_ec / num_standard_ec)
    remainder_actives = num_non_ec % num_standard_ec

    # assign brothers to all non-marshal and non president EC members
    for ec_member in standard_ec_brothers:
        # the remaining brothers that do no divide evenly into the total non ec actives
        # need to be distributed among EC as equally as possible
        if remainder_actives > 0:
            actives_to_assign = actives_per_ec_member + 1
            remainder_actives = remainder_actives - 1
        else:
            actives_to_assign = actives_per_ec_member

        # get the brothers to be assigned to the current ec_member
        assigned_actives = actives[actives_index:actives_index + actives_to_assign]
        actives_index = actives_index + actives_to_assign

        # assign the brothers to the current ec_member
        create_node_with_children(ec_member, president, assigned_actives)

    return HttpResponseRedirect(reverse('dashboard:emergency_phone_tree_view'))


@verify_position(['President', 'Adviser'])
def cleanup_semester(request):

    if request.method == 'POST':
        form = SelectSemester(request.POST)

        if form.is_valid():
            semester = form.cleaned_data['semester']

            delete_all_meet_a_brothers()
            delete_old_events(semester)
            create_unmade_valid_semesters()
            create_chapter_events(semester)

    # TODO: add error handling for false cases?

    return HttpResponseRedirect(reverse('dashboard:home'))
