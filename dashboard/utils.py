from datetime import datetime
from django.contrib.auth.models import User
from .models import *


# get semester used for filtering throughout the views
# based on SEASON_CHOICES in models (0,1,2) => ('Spring','Summer','Fall')
def get_season():
    month = datetime.now().month
    if month <= 5:
        return '0'
    elif month <= 7:
        return '1'
    else:
        return '2'


def get_year():
    return datetime.now().year


def get_month():
    return datetime.now().month


def get_day():
    return datetime.now().day


def verify_president(user):
    # TODO: create custom user with roster_number
    roster_number = user.roster_number
    if Position.objects.filter(roster_number=roster_number)[0].brother.roster_number is roster_number:
        return True
    else:
        return False
