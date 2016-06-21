from django.http import HttpResponse
from django.shortcuts import render
from .models import Brother


def home(request):
    return render(request, 'base.html', {})


def brother(request):
    current_brother = Brother.objects.get(pk=1)
    context = {
        "brother": current_brother,
    }
    return render(request, "brother.html", context)


def president(request):
    return HttpResponse("This will be the President page")


def v_president(request):
    return HttpResponse("This will be the Vice President page")


def treasurer(request):
    return HttpResponse("This will be the Treasurer page")


def secretary(request):
    return HttpResponse("This will be the Secretary page")


def scholarship_c(request):
    brothers = Brother.objects.order_by('last_name')
    context = {
        "brothers": brothers,
    }
    return render(request, "scholarship-chair.html", context)


def recruitment_c(request):
    return HttpResponse("This will be the Recruitment Chair page")


def service_c(request):
    return HttpResponse("This will be the Service Chair page")


def philanthropy_c(request):
    return HttpResponse("This will be the Philanthropy Chair page")


def detail_m(request):
    return HttpResponse("This will be the Detail Manager page")