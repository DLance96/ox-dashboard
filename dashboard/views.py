from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return HttpResponse("This will be the homepage")


def president(request):
    return HttpResponse("This will be the President page")


def v_president(request):
    return HttpResponse("This will be the Vice President page")


def treasurer(request):
    return HttpResponse("This will be the Treasurer page")


def secretary(request):
    return HttpResponse("This will be the Secretary page")


def scholarship_c(request):
    return HttpResponse("This will be the Scholarship Chair page")


def recruitment_c(request):
    return HttpResponse("This will be the Rectuitment Chair page")


def service_c(request):
    return HttpResponse("This will be the Service Chair page")


def philanthropy_c(request):
    return HttpResponse("This will be the Philanthropy Chair page")


def detail_m(request):
    return HttpResponse("This will be the Detail Manager page")