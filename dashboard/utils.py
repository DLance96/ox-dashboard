from datetime import datetime
from django.contrib.auth.models import User
from .models import *


# EC Positions
ec = ['President', 'Vice President', 'Vice President of Health and Safety', 'Secretary', 'Treasurer', 'Marshal',
      'Recruitment Chair', 'Scholarship Chair']
# Positions not on EC that have importance on the dashboard
non_ec = ['Service Chair', 'Philanthropy Chair', 'Detail Manager']


def get_semester():
    semester = Semester.objects.filter(season=get_season(), year=get_year())
    if semester.exists():
        return semester[0]
    else:
        semester = Semester(season=get_season(), year=get_year())
        semester.save()
        return semester

# get semester used for filtering throughout the views
# based on SEASON_CHOICES in models (0,1,2) => ('Spring','Summer','Fall')
def get_season():
    return '0'
    # month = datetime.datetime.now().month
    # if month <= 5:
    #     return '0'
    # elif month <= 7:
    #     return '1'
    # else:
    #     return '2'

def get_season_from(month):
    if month <= 5:
        return '0'
    elif month <= 7:
        return '1'
    else:
        return '2'


def get_year():
    return datetime.datetime.now().year


def get_month():
    return datetime.datetime.now().month


def get_day():
    return datetime.datetime.now().day


def forms_is_valid(form_list):
    for form in form_list:
        if not form.is_valid():
            return False
    return True


def verify_president(user):
    # TODO: create custom user with roster_number
    roster_number = user.roster_number
    if Position.objects.filter(roster_number=roster_number)[0].brother.roster_number is roster_number:
        return True
    else:
        return False
