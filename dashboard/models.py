import datetime
import django.utils.timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator


class Semester(models.Model):
    SEASON_CHOICES = (
        ('0', 'Spring'),
        ('1', 'Summer'),
        ('2', 'Fall'),
    )
    YEAR_CHOICES = []
    for r in range(2010, (datetime.datetime.now().year + 2)):
        YEAR_CHOICES.append((r, r))

    season = models.CharField(
        max_length=1,
        choices=SEASON_CHOICES,
        default='0',
    )
    year = models.IntegerField(
        choices=YEAR_CHOICES,
        default=datetime.datetime.now().year,
    )

    def __str__(self):
        return "%s - %s" % (self.year, self.get_season_display())


class Brother(models.Model):
    user = models.OneToOneField(User, unique=True)

    # General profile information
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    roster_number = models.IntegerField(blank=True, null=True)
    semester_joined = models.ForeignKey(
        Semester, on_delete=models.CASCADE, blank=True, null=True
    )
    date_pledged = models.DateField(blank=True, null=True)

    FRESHMAN = 'FR'
    SOPHOMORE = 'SO'
    JUNIOR = 'JR'
    SENIOR = 'SR'
    FIFTH_YEAR = 'FY'
    ALUMNI = 'AL'

    SCHOOL_STATUS_CHOICES = (
        (FRESHMAN, 'Freshman'),
        (SOPHOMORE, 'Sophomore'),
        (JUNIOR, 'Junior'),
        (SENIOR, 'Senior'),
        (FIFTH_YEAR, 'Fifth Year'),
        (ALUMNI, 'Alumni'),
    )
    school_status = models.CharField(
        max_length=2,
        choices=SCHOOL_STATUS_CHOICES,
        default=FRESHMAN,
    )

    BROTHER_STATUS_CHOICES = (
        ('0', 'Candidate'),
        ('1', 'Brother'),
        ('2', 'Alumni'),
    )

    brother_status = models.CharField(
        max_length=1,
        choices=BROTHER_STATUS_CHOICES,
        default='0',
    )

    # Secretary Information
    major = models.CharField(max_length=200, default="Undecided")
    minor = models.CharField(max_length=200, blank=True, null=True)
    case_ID = models.CharField(max_length=10)
    birthday = models.DateField()
    hometown = models.CharField(max_length=200, default="Cleveland, OH")
    t_shirt_size = models.CharField(max_length=5, default="M")

    # regex for proper phone number entry
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: "
                "'+999999999'. Up to 15 digits allowed.")
    # validators should be a list
    phone_number = models.CharField(
        validators=[phone_regex], blank=True, max_length=15
    )

    # President Information
    emergency_contact = models.CharField(
        max_length=200, default="Chapter President"
    )
    emergency_contact_phone_number = models.CharField(
        validators=[phone_regex], blank=True, max_length=15
    )

    # Vice President Information
    room_number = models.CharField(max_length=3, default="NA")
    address = models.CharField(max_length=200, default="Theta Chi House")

    STANDING_COMMITTEE_CHOICES = {
        ('0', 'Recruitment'),
        ('1', 'Public Relations'),
        ('2', 'Health and Safety'),
        ('3', 'Social'),
        ('4', 'Unassigned')
    }

    OPERATIONAL_COMMITTEE_CHOICES = {
        ('0', 'Alumni Relations'),
        ('1', 'Membership Development'),
        ('2', 'Scholarship'),
        ('3', 'Unassigned')
    }

    standing_committee = models.CharField(
        max_length=1, choices=STANDING_COMMITTEE_CHOICES, default='4'
    )
    operational_committee = models.CharField(
        max_length=1, choices=OPERATIONAL_COMMITTEE_CHOICES, default='3'
    )

    # Treasurer Information
    # TODO: Add treasury models

    # Recruitment Information
    # TODO: determine if there are any recruitment models

    # Service Chair Information
    # TODO: determine if there are any service models

    # Philanthropy Chair Information
    # TODO: determine if there are any philanthropy models

    # Detail Manager Chair Information
    # TODO: determine if there are any detail manager models
    house_detail_buyout = models.BooleanField(default=False)
    kitchen_detail_buyout = models.BooleanField(default=False)
    in_house = models.BooleanField(default=True)

    def __str__(self):
        return (self.first_name + " " + self.last_name).encode('utf8')


class Position(models.Model):
    title = models.CharField(max_length=45)
    ec = models.BooleanField(default=False)
    brother = models.ForeignKey(
        Brother, on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        return self.title.encode('utf8')


class PotentialNewMember(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45, blank=True, null=True)
    case_ID = models.CharField(max_length=10, blank=True, null=True)

    # regex for proper phone number entry
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: "
                "'+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(
        validators=[phone_regex], blank=True, null=True, max_length=15
    )
    # validators should be a list

    primary_contact = models.ForeignKey(
        Brother, on_delete=models.CASCADE, related_name="primary"
        )
    secondary_contact = models.ForeignKey(
        Brother, on_delete=models.CASCADE, blank=True, null=True,
        related_name="secondary"
    )
    tertiary_contact = models.ForeignKey(
        Brother, on_delete=models.CASCADE, blank=True, null=True,
        related_name="tertiary"
    )
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return (self.first_name + " " + self.last_name).encode('utf8')


class ServiceSubmission(models.Model):
    name = models.CharField(max_length=200, default="Service Event")
    description = models.TextField(default="I did the service thing")
    hours = models.IntegerField(default=0)
    date_applied = models.DateTimeField(default=django.utils.timezone.now)

    STATUS_CHOICES = (
        ('0', 'Pending'),
        ('1', 'Awaiting Approval'),
        ('2', 'Approved'),
        ('3', 'Denied'),
    )

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='0',
    )

    date = models.DateField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE)

    def __str__(self):
        return self.name.encode('utf8')


# Given separate section to prevent accidental viewing while in admin views
class ScholarshipReport(models.Model):
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    past_semester_gpa = models.DecimalField(
        max_digits=5, decimal_places=2, default=4.0
    )
    cumulative_gpa = models.DecimalField(
        max_digits=5, decimal_places=2, default=4.0
    )
    scholarship_plan = models.TextField(
        default="Scholarship plan has not been setup yet if you past semester "
                "GPA or cum GPA are below 3.0 you should "
                "setup a meeting to have this corrected"
    )

    def __str__(self):
        return "%s %s - %s %s" % (self.brother.first_name,
                                  self.brother.last_name,
                                  self.semester.get_season_display(),
                                  self.semester.year)


class Event(models.Model):
    name = models.CharField(max_length=200, default="Event")
    date = models.DateField(default=django.utils.timezone.now)
    all_day = models.BooleanField(default=False)
    start_time = models.TimeField(default=datetime.time(hour=0, minute=0))
    end_time = models.TimeField(blank=True, null=True)
    attendees_brothers = models.ManyToManyField(Brother, blank=True)
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE, blank=True, null=True
    )
    notes = models.TextField(blank=True, null=True)
    minutes = models.URLField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name.encode('utf8')


class ChapterEvent(Event):
    mandatory = models.BooleanField(default=True)


class PhilanthropyEvent(Event):
    rsvp_brothers = models.ManyToManyField(Brother, blank=True, related_name="rsvp_philanthropy")


class ServiceEvent(Event):
    rsvp_brothers = models.ManyToManyField(Brother, blank=True, related_name="rsvp_service")


class RecruitmentEvent(Event):
    attendees_pnms = models.ManyToManyField(PotentialNewMember, blank=True)
    rush = models.BooleanField(default=True)


class ScholarshipEvent(Event):
    pass


class StudyTableEvent(Event):
    def __str__(self):
        return "Study Tables - %s" % self.date


COMMITTEE_CHOICES = {
        ('0', 'Recruitment'),
        ('1', 'Public Relations'),
        ('2', 'Health and Safety'),
        ('3', 'Social'),
        ('4', 'Alumni Relations'),
        ('5', 'Membership Development'),
        ('6', 'Scholarship'),
    }


class CommitteeMeetingEvent(Event):
    committee = models.CharField(max_length=1, choices=COMMITTEE_CHOICES)

    def __str__(self):
        return "%s - %s" % (self.get_committee_display(), self.date)


class Excuse(models.Model):
    event = models.ForeignKey(ChapterEvent, on_delete=models.CASCADE)
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(default=django.utils.timezone.now)
    description = models.TextField(
        "Reasoning", default="I will not be attending because"
    )
    response_message = models.TextField(blank=True, null=True)

    STATUS_CHOICES = (
        ('0', 'Pending'),
        ('1', 'Approved'),
        ('2', 'Denied'),
        ('3', 'Non-Mandatory'),
    )

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='0',
    )

    def __str__(self):
        return self.brother.first_name \
            + " " + self.brother.last_name + " - " + self.event.name



class Supplies(models.Model):
    what = models.CharField(max_length=256)
    done = models.BooleanField(default=False)
    when = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.what.encode('utf8')
