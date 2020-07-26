"""How to use:

run

python manage.py.shell

then in that shell import this file and run build_superuser(<your case ID>)

"""

from django.contrib.auth.models import User
from dashboard.views import Position, Brother
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
    "Public Relations Chair"
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
    for title in ALL_POSITIONS:
        new_position = Position()
        new_position.title = title
        new_position.ec = title in EC_POSITIONS
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
