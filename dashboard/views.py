from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
import utils
from .forms import *


def home(request):
    return render(request, 'home.html', {})


def brother_view(request):
    # TODO: pull brother from user login
    # TODO: check if user is authenticated
    current_brother = Brother.objects.filter(roster_number=898).all()[0]
    context = {
        ('brother', current_brother),
    }
    return render(request, "brother.html", context)


def president(request):
    # TODO: verify that user is President
    return render(request, 'president.html', {})


def v_president(request):
    # TODO: verify that user is Vice President
    return render(request, 'vice-president.html', {})


def treasurer(request):
    # TODO: verify that user is Treasurer
    return render(request, 'treasurer.html', {})


def secretary(request):
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
    # TODO: create secretary-event.html with attendance form
    return render(request, "secretary-event.html", context)


def secretary_excuse(request, excuse_id):
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
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    excuses = Excuse.objects.order_by('brother__last_name').order_by('event__date')
    context = {
        'excuses': excuses,
    }
    # TODO: create secretary-excuses-all.html
    return render(request, "home.html", context)


def secretary_add_event(request):
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


# view for seeing all events in the database
def secretary_all_events(request):
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    events = ChapterEvent.objects.all()
    context = {
        'events': events,
    }
    # Reminder to use a for loop for all the years and then have Spring Semester first in secretary-all-events.html
    # TODO: make secretary-all-events.html
    return render(request, "home.html", context)


def scholarship_c(request):
    # TODO: verify that user is Scholarship chair (add a file with scholarship verify function)
    reports = ScholarshipReport.objects.filter(semester__season=utils.get_season(),
                                               semester__year=utils.get_year())\
        .order_by("past_semester_gpa")
    context = {
        'reports': reports,
    }
    return render(request, "scholarship-chair.html", context)


def recruitment_c(request):
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
    # TODO: verify that user is Recruitment Chair
    # TODO: create recruitment-chair-add-event.html
    return render(request, 'home.html', {})


def service_c(request):
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
    # TODO: verify that user is Service Chair
    # TODO: create service-chair-add-event.html
    return render(request, 'home.html', {})


def philanthropy_c(request):
    # TODO: verify that user is Philanthropy Chair
    events = PhilanthropyEvent.objects.filter(semester__season=utils.get_season(),
                                              semester__year=utils.get_year())
    context = {
        'events': events,
    }
    return render(request, 'philanthropy-chair.html', context)


def philanthropy_c_add_event(request):
    # TODO: verify that user is Philanthropy Chair
    # TODO: create philanthropy-chair-add-event.html
    return render(request, 'home.html', {})


def detail_m(request):
    # TODO: verify that user is Detail Manager
    return render(request, 'detail-manager.html', {})
