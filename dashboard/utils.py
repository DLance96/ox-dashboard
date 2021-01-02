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
    """Creates a list of forms, 1 for each brother in eligible_attendees. Each form has 1 field, being a
    checkbox field to determine the attendance of the brother at the event with a label set to the brother's name
    prefix=counter ensures that in the html, the forms have different id's

    """
    brothers = event.eligible_attendees.all()
    brother_form_list = []

    for counter, brother in enumerate(brothers):
        new_form = BrotherAttendanceForm(request.POST or None, initial={'present':  event.attendees_brothers.filter(id=brother.id).exists()},
                                         prefix=counter,
                                         brother="- %s %s" % (brother.first_name, brother.last_name))
        brother_form_list.append(new_form)

    return brothers, brother_form_list


def create_recurring_meetings(instance, committee):
    date = datetime.datetime.now()
    try:
        semester = Semester.objects.filter(season=get_season_from(date.month),
                                           year=date.year)[0]
    except IndexError:
        semester = Semester(season=get_season_from(date.month),
                            year=date.year)
        semester.save()

    if date.weekday() >= instance['meeting_day']:
        date_offset = 7 + instance['meeting_day'] - date.weekday()
    elif date.weekday() < instance['meeting_day']:
        date_offset = instance['meeting_day'] - date.weekday()
    date = date + datetime.timedelta(days=date_offset)
    start_date = date
    end_date = date
    if semester.season == '2':
        end_date = datetime.datetime(date.year, 12, 31)
    elif semester.season == '0':
        end_date = datetime.datetime(date.year, 5, 31)
    day_count = int((end_date - start_date).days / instance['meeting_interval']) + 1
    committee_object = Committee.objects.get(committee=committee)
    for date in (start_date + datetime.timedelta(instance['meeting_interval']) * n for n in range(day_count)):
        event = CommitteeMeetingEvent(date=date, start_time=instance['meeting_time'], semester=semester,
                                      committee=committee_object, recurring=True)
        event.save()
        event.eligible_attendees.set(committee_object.members.order_by('last_name'))
        event.save()


def create_node_with_children(node_brother, notified_by, brothers_notified):
    PhoneTreeNode(brother=node_brother, notified_by=notified_by).save()

    for brother in brothers_notified:
        PhoneTreeNode(brother=brother, notified_by=node_brother).save()


def notifies(brother):
    return list(map(lambda node : node.brother, PhoneTreeNode.objects.filter(notified_by=brother)))


def notified_by(brother):
    node = PhoneTreeNode.objects.filter(brother=brother)
    return node[0].notified_by if len(node) > 0 else None


def create_attendance_list(events, excuses_pending, excuses_approved, brother):
    """zips together a list of tuples where the first element is each event and the second is the brother's
    status regarding the event. If the event hasn't occurred, the status is blank, if it's not a mandatory
    event it's 'not mandatory'

    :param list[Event] events:
        a list of events you want to create this attendance list for

    :param list[Event] excuses_pending:
        a list of events that the brother has excuses created for that are currently pending

    :param list[Event] excuses_approved:
        a list of events that the brother has excuses created for that are approved

    :param Brother brother:
        which brother the excuses are for

    :returns:
        a zipped list of events and its corresponding attendance
    :rtype: list[Event, str]

    """
    attendance = []
    for event in events:
        if int(event.date.strftime("%s")) > int(datetime.datetime.now().strftime("%s")):
            attendance.append('')
        elif not event.mandatory:
            attendance.append('Not Mandatory')
        else:
            if event.attendees_brothers.filter(id=brother.id):
                attendance.append('Attended')
            elif event.pk in excuses_approved:
                attendance.append('Excused')
            elif event.pk in excuses_pending:
                attendance.append('Pending')
            else:
                attendance.append('Unexcused')

    return zip(events, attendance)


def mark_attendance_list(brother_form_list, brothers, event):
    """Mark the attendance for the given brothers at the given event

    :param list[BrotherAttendanceForm] brother_form_list:
        a list of forms which holds the marked attendance for the brother it's associated with

    :param list[Brother] brothers:
        a list of brothers, values must correspond to the same order as it was used to create the brother_form_list

    :param Event event:
        the event that has its attendance being marked

    """
    for counter, form in enumerate(brother_form_list):
        instance = form.cleaned_data
        if instance['present'] is True:
            event.attendees_brothers.add(brothers[counter])
            event.save()
            # if a brother is marked present, deletes any of the excuses associated with this brother and this event
            excuses = Excuse.objects.filter(brother=brothers[counter], event=event)
            if excuses.exists():
                for excuse in excuses:
                    excuse.delete()
        if instance['present'] is False:
            event.attendees_brothers.remove(brothers[counter])
            event.save()


def update_eligible_brothers(instance, event):
    # for each brother selected in the add brothers field, add them to eligible_attendees
    if instance['add_brothers']:
        event.eligible_attendees.add(*instance['add_brothers'].values_list('pk', flat=True))
    # for each brother selected in the add brothers field, remove them from eligible_attendees
    # and the attended brothers list
    if instance['remove_brothers']:
        event.eligible_attendees.remove(*[o.id for o in instance['remove_brothers']])
        event.attendees_brothers.remove(*[o.id for o in instance['remove_brothers']])
    event.save()


def save_event(instance, eligible_attendees):
    semester, created = Semester.objects.get_or_create(season=get_season_from(instance.date.month),
                                      year=instance.date.year)
    instance.semester = semester
    instance.save()
    # you must save the instance into the database as a row in the table before you can set the manytomany field
    instance.eligible_attendees.set(eligible_attendees)
    instance.save()
