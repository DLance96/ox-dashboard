from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import utils
from .forms import *
from django.views.generic import View
from django.contrib import auth


class LoginView(View):
    """ Logs in and redirects to the homepage """
    def post(self, request, *args, **kwargs):
        user = auth.authenticate(
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user is not None:
            print user.is_active
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


def home(request):
    """ Renders the home page """
    context = {
    }
    return render(request, 'home.html', context)


def brother_view(request):
    """ Renders the brother page of current user showing all standard brother information """
    # TODO: pull brother from user login
    # TODO: check if user is authenticated
    current_brother = Brother.objects.filter(roster_number=989).all()[0]
    context = {
        ('brother', current_brother),
    }
    return render(request, "brother.html", context)


def president(request):
    """ Renders the President page and all relevant information """
    # TODO: verify that user is President
    return render(request, 'president.html', {})


def vice_president(request):
    """ Renders the Vice President page and all relevant information, primarily committee related """
    # TODO: verify that user is Vice President
    return render(request, 'vice-president.html', {})


def treasurer(request):
    """ Renders all the transactional information on the site for the treasurer """
    # TODO: verify that user is Treasurer
    return render(request, 'treasurer.html', {})


def secretary(request):
    """ Renders the secretary page giving access to excuses and ChapterEvents """
    # TODO: verify that user is Secretary
    excuses = Excuse.objects.filter(event__semester__season=utils.get_season(),
                                    event__semester__year=utils.get_year(),
                                    status='0').order_by("event__date")
    events = ChapterEvent.objects.filter(semester__season=utils.get_season(),
                                         semester__year=utils.get_year()).order_by("date")
    context = {
        'excuses': excuses,
        'events': events,
    }
    return render(request, 'secretary.html', context)


# View for doing attendance on a specific event
def secretary_event(request, event_id):
    """ Renders the attendance sheet for any event """
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    event = ChapterEvent.objects.get(pk=event_id)
    brothers = Brother.objects.exclude(brother_status='2')
    form_list = []
    for brother in brothers:
        if event.attendees.filter(roster_number=brother.roster_number):
            new_form = AttendanceForm(request.POST or None, initial={'present': True}, prefix=brother.roster_number,
                                      brother="- %s %s" % (brother.first_name, brother.last_name))
            form_list.append(new_form)
        else:
            new_form = AttendanceForm(request.POST or None, initial={'present': False}, prefix=brother.roster_number,
                                      brother="- %s %s" % (brother.first_name, brother.last_name))
            form_list.append(new_form)
    list = zip(brothers, form_list)

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
        'list': list,
        'event': event,
    }
    return render(request, "secretary-event.html", context)


def secretary_excuse(request, excuse_id):
    """ Renders Excuse response form """
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    excuse = get_object_or_404(Excuse, pk=excuse_id)
    form = ExcuseResponseForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            instance = form.save(commit=False)
            print instance.response_message
            print instance.status
            if instance.status == '2':
                context = {
                    'excuse': excuse,
                    'form': form,
                    'error_message': "Response message required for denial"
                }
                return render(request, "secretary-excuse.html", context)
            else:
                excuse.status = instance.status
                excuse.response_message = instance.response_message
                excuse.save()
                return HttpResponseRedirect(reverse('dashboard:secretary'))

    context = {
        'excuse': excuse,
        'form': form,
    }
    return render(request, "secretary-excuse.html", context)


def secretary_all_excuses(request):
    """ Renders all excuses sorted by date then semester """
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    excuses = Excuse.objects.order_by('brother__last_name').order_by('event__date')
    context = {
        'excuses': excuses,
    }
    # TODO: create secretary-excuses-all.html
    return render(request, "home.html", context)


def secretary_view_event(request, event_id):
    """ Renders the Secretary way of viewing old events """
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    event = ChapterEvent.objects.get(pk=event_id)
    attendees = event.attendees.all().order_by("last_name")

    context = {
        'position': "Secretary",
        'attendees': attendees,
        'event': event,
    }
    return render(request, "chapter-view-event.html", context)


def secretary_brother_list(request):
    """ Renders the Secretary way of viewing brothers """
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    brothers = Brother.objects.exclude(brother_status='2')
    context = {
        'position': 'Secretary',
        'brothers': brothers
    }
    return render(request, "brother-list.html", context)


def secretary_brother_view(request, brother_id):
    """ Renders the Secretary way of viewing a brother """
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    brother = Brother.objects.get(pk=brother_id)
    context = {
        'position': 'Secretary',
        'brother': brother
    }
    return render(request, "home.html", context)


def secretary_brother_edit(request, brother_id):
    """ Renders the Secretary way of editing brother info """
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    brother = Brother.objects.get(pk=brother_id)
    form = None  # TODO: create UpdateForm

    context = {
        'position': 'Secretary',
        'brother': brother,
        'form': form
    }
    return render(request, "home.html", context)


def secretary_add_event(request):
    """ Renders the Secretary way of adding ChapterEvents """
    # TODO: verify that user is Secretary (add a file with secretary verify function)
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


def secretary_all_events(request):
    """ Renders a secretary view with all the ChapterEvent models ordered by date grouped by semester """
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    events_by_semester = []
    semesters = Semester.objects.order_by("season").order_by("year").all()
    for semester in semesters:
        events = ChapterEvent.objects.filter(semester=semester).order_by("date")
        if len(events) == 0:
            print semester
            print events
            events_by_semester.append([])
        else:
            print semester
            print events
            events_by_semester.append(events)
    zip_list = zip(events_by_semester, semesters)
    context = {
        'list': zip_list,
        'position': "Secretary"
    }
    return render(request, "chapter-all-events.html", context)


def marshall(request):
    """ Renders the Marshall page listing all the candidates and relevant information to them """
    # TODO: verify that user is Marshall
    candidates = Brother.objects.filter(brother_status='0')
    context = {
        'candidates': candidates,
    }
    return render(request, 'marshall.html.html', context)


def scholarship_c(request):
    """ Renders the Scholarship page listing all brother gpas and study table attendance """
    # TODO: verify that user is Scholarship chair (add a file with scholarship verify function)
    reports = ScholarshipReport.objects.filter(semester__season=utils.get_season(),
                                               semester__year=utils.get_year()) \
        .order_by("past_semester_gpa")
    context = {
        'reports': reports,
    }
    return render(request, "scholarship-chair.html", context)


def recruitment_c(request):
    """ Renders Scholarship chair page with events for the current and following semester """
    # TODO: verify that user is Recruitment Chair
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


def recruitment_c_add_event(request):
    """ Renders the recruitment chair way of adding RecruitmentEvents """
    # TODO: verify that user is Recruitment Chair
    # TODO: create recruitment-chair-add-event.html
    return render(request, 'home.html', {})


def service_c(request):
    """ Renders the service chair page with service submissions """
    # TODO: verify that user is Service Chair
    events = ServiceEvent.objects.filter(semester__season=utils.get_season(),
                                         semester__year=utils.get_year())
    submissions = ServiceSubmission.objects.filter(semester__season=utils.get_season(),
                                                   semester__year=utils.get_year())
    context = {
        'events': events,
        'submissions': submissions,
    }
    return render(request, 'service-chair.html', context)


def service_c_add_event(request):
    """ Renders the service chair way of adding ServiceEvent """
    # TODO: verify that user is Service Chair
    # TODO: create service-chair-add-event.html
    return render(request, 'home.html', {})


def philanthropy_c(request):
    """ Renders the philanthropy chair's RSVP page for different events """
    # TODO: verify that user is Philanthropy Chair
    events = PhilanthropyEvent.objects.filter(semester__season=utils.get_season(),
                                              semester__year=utils.get_year())
    context = {
        'events': events,
    }
    return render(request, 'philanthropy-chair.html', context)


def philanthropy_c_add_event(request):
    """ Renders the philanthropy chair way of adding PhilanthropyEvent """
    # TODO: verify that user is Philanthropy Chair
    # TODO: create philanthropy-chair-add-event.html
    return render(request, 'home.html', {})


def detail_m(request):
    """ Renders the detail manager page"""
    # TODO: verify that user is Detail Manager
    return render(request, 'detail-manager.html', {})
