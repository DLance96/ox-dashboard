from django.shortcuts import render
from .models import *
import utils


def home(request):
    return render(request, 'home.html', {})


def brother(request):
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
    excuses = EventExcuse.objects.filter(semester__season=utils.get_season(),
                                         semester__year=utils.get_year())
    events = ChapterEvent.objects.filter(date_time__month=utils.get_month(),
                                         date_time__day=utils.get_day(),
                                         date_time__year=utils.get_year())
    context = {
        'excuses': excuses,
        'events': events,
    }
    return render(request, 'secretary.html', context)


# View for doing attendance on a specific event
def secretary_event(request, event_id):
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    event = ChapterEvent.objects.get(pk=event_id)
    context = {
        'event': event,
    }
    # TODO: create secretary-event.html with attendance form
    return render(request, "home.html", context)


def secretary_add_event(request):
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    context = {}
    return render(request, "home.html", context)


# view for seeing all events in the database
def secretary_all_events(request):
    # TODO: verify that user is Secretary (add a file with secretary verify function)
    events = ChapterEvent.objects.all()
    context = {
        'events': events,
    }
    return render(request, "home.html", context)
    # Reminder to use a for loop for all the years and then have Spring Semester first in secretary-all-events.html


def scholarship_c(request):
    # TODO: verify that user is Scholarship chair (add a file with scholarship verify function)
    brothers = Brother.objects.filter(brother_status='1').order_by('last_name')
    context = {
        'brothers': brothers,
    }
    return render(request, "scholarship-chair.html", context)


def recruitment_c(request):
    # TODO: verify that user is Recruitment Chair
    current_season = utils.get_season()
    if current_season is 0:
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
