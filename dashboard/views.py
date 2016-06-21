from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime
from .models import Brother, EventExcuse, ChapterEvent, Semester, ServiceSubmission


# get semester used for filtering throughout the views
# based on SEASON_CHOICES in models (0,1,2) => ('Spring','Summer','Fall')
def get_semester():
    month = datetime.now().month
    if month <= 5:
        return '0'
    elif month <= 7:
        return '1'
    else:
        return '2'


def home(request):
    return render(request, 'home.html', {})


def brother(request):
    # TODO: pull brother from user login
    # TODO: check if user is authenticated
    current_brother = Brother.objects.get(pk=1)
    context = {
        "brother": current_brother,
    }
    return render(request, "brother.html", context)


def president(request):
    # TODO: verify that user is President
    return HttpResponse("This will be the President page")


def v_president(request):
    # TODO: verify that user is Vice President
    return HttpResponse("This will be the Vice President page")


def treasurer(request):
    # TODO: verify that user is Treasurer
    return HttpResponse("This will be the Treasurer page")


def secretary(request):
    # TODO: verify that user is Secretary
    return HttpResponse("This will be the Secretary page")


# View for doing attendance on a specific event
def secretary_event(request, event_id):
    # TODO: verify that user is Secretary
    event = ChapterEvent.objects.get(pk=event_id)
    return HttpResponse("This is the Sectary event page for %s" % event.name)


def scholarship_c(request):
    # TODO: verify that user is Scholarship chair
    brothers = Brother.objects.filter(brother_status='1').order_by('last_name')
    context = {
        "brothers": brothers,
    }
    return render(request, "scholarship-chair.html", context)


def recruitment_c(request):
    # TODO: verify that user is Recruitment Chair
    return HttpResponse("This will be the Recruitment Chair page")


def service_c(request):
    # TODO: verify that user is Service Chair
    submissions = ServiceSubmission.objects.filter(semester__year=datetime.now().year, semester__season=get_semester())
    context = {
        "submissions": submissions,
    }
    return HttpResponse("This will be the Service Chair page for semester %s - %s"
                        % (submissions.all()[0].semester.get_season_display(), datetime.now().year))


def philanthropy_c(request):
    # TODO: verify that user is Philanthropy Chair
    return HttpResponse("This will be the Philanthropy Chair page")


def detail_m(request):
    # TODO: verify that user is Detail Manager
    return HttpResponse("This will be the Detail Manager page")