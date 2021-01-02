"""How to use:

run

python manage.py.shell

then in that shell import this file and run build_superuser(<your case ID>)

"""

from django.contrib.auth.models import User
from dashboard.views import Position, Brother
from dashboard.models import Semester
import datetime

EC_POSITIONS = [
    "President",
    "Vice President",
    "Vice President of Health and Safety",
    "Secretary",
    "Treasurer",
    "Marshal",
    "Recruitment Chair",
    "Scholarship Chair",
]

NON_EC_POSITIONS = [
    "Service Chair",
    "Philanthropy Chair",
    "Detail Manager",
    "Public Relations Chair",
    "Alumni Relations Chair",
    "Social Chair",
    "Membership Development Chair",
    "Community Standards Chair",
    "OX Roast Chair",
    "Damage Chair",
    "Greek Games Chair",
    "Historian",
    "First Guard",
    "Second Guard",
    "Internal Change Chair",
    "Standards Board Justice",
    "Executive Council Member At Large",
    "House Manager",
    "Risk Manager",
    "IFC Rep",
    "Awards Chair",
    "Food Steward",
    "Athletics Chair",
    "Dashboard Chair",
    "Adviser",
]

ALL_POSITIONS = EC_POSITIONS + NON_EC_POSITIONS

def create_django_superuser(username):
    user = User()
    user.username = username
    user.is_staff = True
    user.is_admin = True
    user.is_superuser = True
    user.save()

    return user

def create_superbrother(user):
    new_brother = Brother()
    new_brother.user = user
    new_brother.first_name = "fillmein"
    new_brother.last_name = "fillmein"
    new_brother.case_ID = user.username
    new_brother.birthday = datetime.date.today()
    new_brother.save()

def create_positions():
    for title, _ in Position.PositionChoices.choices:
        new_position = Position()
        new_position.title = title
        new_position.save()

def add_user_to_all_positions(user):
    for position in Position.objects.all():
        position.brothers.add(user.brother)
        position.save()


def build_superuser(username):
    user = create_django_superuser(username)

    create_superbrother(user)

    create_positions()

    add_user_to_all_positions(user)

def make_user_super(username):
    user = User.objects.get(username=username)
    user.is_staff = True
    user.is_admin = True
    user.is_superuser = True
    user.save()

def add_semesters():
    for year in Semester.YEAR_CHOICES:
        for season in Semester.SEASON_CHOICES:
            sem = Semester()
            sem.year = year[0]
            sem.season = season[0]
            sem.save()

# add all the brothers in the given csv file path
# the file should have each line as the following
# firstname,lastname,caseid
# and make sure there is a new line at the end
def add_all_brothers(csvpath, assume_users_exist=False):
    lines = []
    with open(csvpath, "r") as inp:
        lines = inp.readlines()

    for line in lines:
        first, last, caseid = line.split(",")
        # strip newline
        caseid = caseid[:-1]
        if assume_users_exist:
            user = User.objects.get(username=caseid)
        else:
            user = User()
            user.username = caseid
            user.save()

        add_brother(first, last, user)

def add_brother(first, last, user):
    new_brother = Brother()
    new_brother.user = user
    new_brother.first_name = first
    new_brother.last_name = last
    new_brother.case_ID = user.username
    new_brother.birthday = datetime.date.today()
    new_brother.save()

