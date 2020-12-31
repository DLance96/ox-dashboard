from datetime import datetime
from urllib.parse import quote_plus

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.core.handlers.wsgi import WSGIRequest

from .forms import BrotherAttendanceForm
from .models import *

import requests
import re

# EC Positions
all_positions = [
    'President', 'Vice President', 'Vice President of Health and Safety',
    'Secretary', 'Treasurer', 'Marshal', 'Recruitment Chair',
    'Scholarship Chair', 'Service Chair', 'Philanthropy Chair',
    'Detail Manager', 'Alumni Relations Chair',
    'Membership Development Chair', 'Social Chair', 'Public Relations Chair'
]

has_committee = [
    'Vice President of Health and Safety', 'Recruitment Chair',
    'Scholarship Chair', 'Philanthropy Chair', 'Alumni Relations Chair',
    'Membership Development Chair', 'Social Chair', 'Public Relations Chair'
]

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


def do_verify(pos, user):
    if pos == 'ec' and Position.objects.get(brothers__user=user).in_ec:
        return True
    brothers = Position.objects.get(title=pos).brothers.all()
    if user.brother in brothers:
        return True
    return False


def verify_position(positions):
    def verify_decorator(f):
        def error(request):
            e = "Access denied. Only %s may access this page" % ", ".join(
                positions
            )
            messages.error(request, e)
            return HttpResponseRedirect(reverse('dashboard:home'))

        def wrapper(*args, **kwargs):
            request = None
            for a in args:
                if type(a) == WSGIRequest:
                    request = a
                    break

            for pos in positions:
                try:
                    if do_verify(pos, request.user):
                        return f(*args, **kwargs)
                except AttributeError as e:
                    print(
                        'Warning: error when verifying position. Denying. '
                        'Error: %s' % e
                    )
                    return error(request)

            return error(request)

        return wrapper
    return verify_decorator


def committee_meeting_panel(position_name):
    position = Position.objects.get(title=position_name)
    committee = position.committee
    committee_meetings = committee.meetings.all().filter(semester=get_semester()).order_by("start_time")\
                                                 .order_by("date")
    context = {
        'committee_meetings': committee_meetings,
        'position': position,
        'committee': committee,
    }

    return committee_meetings, context


def verify_brother(brother, user):
    """ Verify user is the same as brother """
    return user.brother.id == brother.id


def build_thursday_detail_email(thursday_detail, host):
    """Builds an email (w/ subject) for a Thursday detail"""
    done_link = host + reverse(
        'dashboard:finish_thursday', args=[thursday_detail.pk]
    )
    det_managers = Position.objects.get(title="Detail Manager").brothers.all()
    to = [thursday_detail.brother.user.email]

    email = "Dear %s, \n\n\n" % thursday_detail.brother.first_name

    email += "Your detail is:\n\n"
    email += thursday_detail.full_text()

    email += "\n"
    email += "Please complete it by the required time on the due date and " + \
        "mark it done by midnight.\n\n"
    email += "Go to this link to mark it done: %s\n\n\n" % done_link

    email += "L&R&Cleaning\n--\n%s" % ", ".join([b.first_name for b in det_managers])

    subject = "[DETAILS] %s - %s" % (
        thursday_detail.due_date, thursday_detail.short_description
    )

    return subject, email, to


def build_sunday_detail_email(sunday_group_detail, host):
    brothers = sunday_group_detail.group.brothers.all()
    details = sunday_group_detail.details.all()
    due = details[0].due_date
    det_managers = Position.objects.get(title="Detail Manager").brothers.all()
    done_link = host + reverse(
        'dashboard:finish_sunday', args=[sunday_group_detail.pk]
    )
    to = [b.user.email for b in sunday_group_detail.group.brothers.all()]

    email = "Dear %s, \n\n\n" % ", ".join(
        [b.first_name for b in brothers.all()]
    )

    email += "Your Sunday details are:\n\n"
    for det in details:
        email += det.full_text()
        email += "\n"

    email += "Please complete them before the required time on the due " + \
        "date and make the ones you do as done by midnight.\n\n"
    email += "Go to this link to mark them done: %s\n\n\n" % done_link

    email += "L&R&Cleaning\n--\n%s" % ", ".join([b.first_name for b in det_managers])

    subject = "[DETAILS] Sunday details for %s" % due

    return subject, email, to


def fine_generator():
    x = 5
    while x < 25:
        yield x
        x += 5
    while True:
        yield x


def calc_fines_helper(num_missed):
    gen = fine_generator()
    f = 0
    for _ in range(num_missed):
        f += gen.next()

    return f


def calc_fines(brother):
    missed_thursday_num = len(ThursdayDetail.objects.filter(
        brother=brother, done=False, due_date__lt=datetime.datetime.now()
    ))

    sunday_group = DetailGroup.objects.filter(
        brothers=brother, semester=get_semester()
    )

    sunday_details = SundayGroupDetail.objects.filter(
        group=sunday_group, due_date__lt=datetime.datetime.now()
    )

    missed_sunday_num = len([e for e in sunday_details if not e.done()])

    fine = calc_fines_helper(missed_thursday_num + missed_sunday_num)

    return fine


def photo_context(photo_class):
    photo_urls = []
    for photo in photo_class.objects.all():
        photo_urls.append(photo.photo.url)

    context = {
        'photo_urls': photo_urls
    }

    return context


def photo_form(form_class, request):
    form = form_class(request.POST or None)

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)

        # NOTE: If we move to a CDN instead of storing files with the server,
        # we can probably use this form, but not save the value (set form.save()
        # to form.save(commit=False)) and instead get the url or path from the returned
        # instance and then upload that file to the CDN
        if form.is_valid():
            # TODO: add error handling to stop user from uploading too many photos
            instance = form.save()
            return HttpResponseRedirect(reverse('dashboard:home'))

    return form


def attendance_list(request, event):
    brothers = Brother.objects.exclude(brother_status='2').order_by('last_name')
    brother_form_list = []

    for counter, brother in enumerate(brothers):
        new_form = BrotherAttendanceForm(request.POST or None, initial={'present':  event.attendees_brothers.filter(id=brother.id).exists()},
                                         prefix=counter,
                                         brother="- %s %s" % (brother.first_name, brother.last_name))
        brother_form_list.append(new_form)

    return brothers, brother_form_list


def semester_end_date(season, year, treat_summer_fall_as_same=True):
    # if spring semester, use may as the end month
    if season == '0':
        end_month = 5
    elif season == '1' and not treat_summer_fall_as_same:
        end_month = 7
    # otherwise, we are in the summer or fall semester, so use december as end month
    else:
        end_month = 12

    # last day of both May, July, and December is the 31st.
    last_day_of_month = 31

    return datetime.datetime(year, end_month, last_day_of_month)


def semester_start_date(season, year):
    # Find the start month for the semester season
    start_month = {
        '0': 1,
        '1': 6,
        '2': 8
    }.get(season)

    start_day_of_month = 1

    return datetime.datetime(year, start_month, start_day_of_month)

# TODO: this is already accomplished by get_semester
def current_semester(current_date):
    try:
        semester = Semester.objects.filter(season=get_season_from(current_date.month),
                                           year=current_date.year)[0]
    except IndexError:
        semester = Semester(season=get_season_from(current_date.month),
                            year=current_date.year)
        semester.save()

    return semester

def create_recurring_events(begin_date, day, interval, event_constructor):
    date = begin_date
    semester = current_semester(date)

    # offset to the next week
    if date.weekday() >= day:
        date_offset = 7 + day - date.weekday()
    # otherwise use this week
    elif date.weekday() < day:
        date_offset = day - date.weekday()

    date = date + datetime.timedelta(days=date_offset)
    start_date = date
    end_date = semester_end_date(semester.season, date.year)

    day_count = int((end_date - start_date).days / interval) + 1
    for date in (start_date + datetime.timedelta(interval) * n for n in range(day_count)):
        event = event_constructor(date, semester)
        event.save()

def create_recurring_meetings(instance, committee):
    create_recurring_events(
        datetime.datetime.now(),
        instance['meeting_day'],
        instance['meeting_interval'],
        lambda date, semester: CommitteeMeetingEvent(
            date=date,
            start_time=instance['meeting_time'],
            semester=semester,
            committee=Committee.objects.get(committee=committee),
            recurring=True
        ))

def create_node_with_children(node_brother, notified_by, brothers_notified):
    PhoneTreeNode(brother=node_brother, notified_by=notified_by).save()

    for brother in brothers_notified:
        PhoneTreeNode(brother=brother, notified_by=node_brother).save()


def notifies(brother):
    return list(map(lambda node : node.brother, PhoneTreeNode.objects.filter(notified_by=brother)))

def notified_by(brother):
    node = PhoneTreeNode.objects.filter(brother=brother)
    return node[0].notified_by if len(node) > 0 else None

def delete_all_meet_a_brothers():
    MeetABrother.objects.all().delete()

def delete_old_events(semester):
    current_date = datetime.datetime.now()
    start_date = semester_start_date(semester.season, semester.year)
    old_events = Event.objects.filter(date__lt=start_date)

    old_events.delete()

def create_unmade_valid_semesters():
    for year, _ in Semester.YEAR_CHOICES:
        for season, _ in Semester.SEASON_CHOICES:
            if not Semester.objects.filter(season=season, year=year).exists():
                sem = Semester()
                sem.year = year
                sem.season = season
                sem.save()

def create_chapter_events(semester):
    sunday = 6

    create_recurring_events(
        semester_start_date(semester.season, semester.year),
        sunday,
        Committee.MeetingIntervals.WEEKLY,
        lambda date, semester: ChapterEvent(
            date=date,
            start_time=Event.TimeChoices.T_18_30,  # 6:30 PM
            end_time=Event.TimeChoices.T_20_30,  # 8:30 PM
            semester=semester,
        ))
