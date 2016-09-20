from datetime import datetime

from .models import *

# EC Positions
ec = ['President', 'Vice President', 'Vice President of Health and Safety', 'Secretary', 'Treasurer', 'Marshal',
      'Recruitment Chair', 'Scholarship Chair']
# Positions not on EC that have importance on the dashboard
non_ec = ['Service Chair', 'Philanthropy Chair', 'Detail Manager']

# Toggle dependant on whether you want position verification
# if os.environ.get('DEBUG'):
#     debug = os.environ.get('DEBUG')
# else:
#     debug = True
debug = False


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
    # return '0'
    month = datetime.datetime.now().month
    if debug:
        return '0'
    else:
        if month <= 5:
            return '0'
        elif month <= 7:
            return '1'
        else:
            return '2'


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
    """ Verify user has President permissions """
    user_id = user.brother.id
    if Position.objects.filter(title='President')[0].brother.id == user_id or \
            debug:
        return True
    else:
        return False


def verify_vice_president(user):
    """ Verify user has Vice President permissions """
    user_id = user.brother.id
    if Position.objects.filter(title='President')[0].brother.id == user_id or \
        Position.objects.filter(title='Vice President')[0].brother.id == user_id or \
            debug:
        return True
    else:
        return False


def verify_vphs(user):
    """ Verify user has Vice President of Health and Safety permissions """
    user_id = user.brother.id
    if Position.objects.filter(title='President')[0].brother.id == user_id or \
        Position.objects.filter(title='Vice President')[0].brother.id == user_id or \
        Position.objects.filter(title='Vice President of Health and Safety')[0].brother.id == user_id or \
            debug:
        return True
    else:
        return False


def verify_secretary(user):
    """ Verify user has Secretary permissions """
    user_id = user.brother.id
    if Position.objects.filter(title='President')[0].brother.id == user_id or \
        Position.objects.filter(title='Vice President')[0].brother.id == user_id or \
        Position.objects.filter(title='Secretary')[0].brother.id == user_id or \
            debug:
        return True
    else:
        return False


def verify_treasurer(user):
    """ Verify user has Treasurer permissions """
    user_id = user.brother.id
    if Position.objects.filter(title='President')[0].brother.id == user_id or \
        Position.objects.filter(title='Treasurer')[0].brother.id == user_id or \
            debug:
        return True
    else:
        return False


def verify_marshal(user):
    """ Verify user has Marshal permissions """
    user_id = user.brother.id
    if Position.objects.filter(title='President')[0].brother.id == user_id or \
        Position.objects.filter(title='Vice President')[0].brother.id == user_id or \
        Position.objects.filter(title='Marshal')[0].brother.id == user_id or \
            debug:
        return True
    else:
        return False


def verify_recruitment_chair(user):
    """ Verify user has Recruitment Chair permissions """
    user_id = user.brother.id
    if Position.objects.filter(title='President')[0].brother.id == user_id or \
        Position.objects.filter(title='Vice President')[0].brother.id == user_id or \
        Position.objects.filter(title='Recruitment Chair')[0].brother.id == user_id or \
            debug:
        return True
    else:
        return False


def verify_scholarship_chair(user):
    """ Verify user has Scholarship Chair permissions """
    user_id = user.brother.id
    if Position.objects.filter(title='President')[0].brother.id == user_id or \
        Position.objects.filter(title='Scholarship Chair')[0].brother.id == user_id or \
            debug:
        return True
    else:
        return False


def verify_service_chair(user):
    """ Verify user has Service Chair permissions """
    user_id = user.brother.id
    if Position.objects.filter(brother__id=user_id)[0].ec or \
        Position.objects.filter(title='Service Chair')[0].brother.id == user_id or \
            debug:
        return True
    else:
        return False


def verify_philanthropy_chair(user):
    """ Verify user has Philanthropy Chair permissions """
    user_id = user.brother.id
    if Position.objects.filter(brother__id=user_id)[0].ec or \
        Position.objects.filter(title='Philanthropy Chair')[0].brother.id == user_id or \
            debug:
        return True
    else:
        return False


def verify_detail_manager(user):
    """ Verify user has Detail Manager permissions """
    user_id = user.brother.id
    if Position.objects.filter(brother__id=user_id)[0].ec or \
        Position.objects.filter(title='Detail Manager')[0].brother.id == user_id or \
            debug:
        return True
    else:
        return False


def verify_brother(brother, user):
    """ Verify user is the same as brother """
    if user.brother.id == brother.id:
        return True
    else:
        return False
