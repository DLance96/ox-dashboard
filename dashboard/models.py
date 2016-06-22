from django.db import models
from django.core.validators import RegexValidator
import datetime


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
    # General profile information
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45)
    roster_number = models.IntegerField(default=1856)
    semester_joined = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)

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
        default=0,
    )

    # Secretary Information
    case_ID = models.CharField(max_length=200)
    birthday = models.DateField()
    hometown = models.CharField(max_length=200, default="Cleveland, OH")

    # regex for proper phone number entry
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: "
                                         "'+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], blank=True, max_length=15)  # validators should be a list

    # Vice President Information
    room_number = models.CharField(max_length=3, default="NA")
    current_residence = models.CharField(max_length=200, default="Theta Chi House")
    standing_committee = models.CharField(max_length=200, default="Not assigned")
    operational_committee = models.CharField(max_length=200, default="Not assigned")

    # Treasurer Information
    # TODO: Add treasury models

    # Recruitment Information
    # TODO: determine if there are any recruitment models

    # Scholarship Information
    past_semester_gpa = models.DecimalField(max_digits=5, decimal_places=2, default=4.0)
    cumulative_gpa = models.DecimalField(max_digits=5, decimal_places=2, default=4.0)
    scholarship_plan = models.TextField(default="Scholarship plan has not been setup yet if you past semester GPA "
                                                "or cum GPA are below 3.0 you should "
                                                "setup a meeting to have this corrected")

    # Service Chair Information
    # TODO: determine if there are any service models

    # Philanthropy Chair Information
    # TODO: determine if there are any philanthropy models

    # Detail Manager Chair Information
    # TODO: determine if there are any detail manager models

    def __str__(self):
        return self.first_name + " " + self.last_name


class Position(models.Model):
    title = models.CharField(max_length=45)
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE)


class PotentialNewMember(models.Model):
    first_name = models.CharField(max_length=45)
    last_name = models.CharField(max_length=45, null=True)
    email = models.EmailField()

    # regex for proper phone number entry
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format: "
                                         "'+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], blank=True, max_length=15)  # validators should be a list

    primary_contact = models.ForeignKey(Brother, on_delete=models.CASCADE, related_name="primary")
    secondary_contact = models.ForeignKey(Brother, on_delete=models.CASCADE, null=True, related_name="secondary")
    tertiary_contact = models.ForeignKey(Brother, on_delete=models.CASCADE, null=True, related_name="tertiary")


class ServiceSubmission(models.Model):
    name = models.CharField(max_length=200, default="Service Event")
    description = models.TextField(default="I did the service thing")
    hours = models.IntegerField(default=0)
    submitted = models.BooleanField(default=False)
    date = models.DateField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ChapterEvent(models.Model):
    name = models.CharField(max_length=200, default="Chapter Event")
    date_time = models.DateTimeField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    mandatory = models.BooleanField(default=True)
    attendees = models.ManyToManyField(Brother)

    def __str__(self):
        return self.name


class PhilanthropyEvent(models.Model):
    name = models.CharField(max_length=200, default="Philanthropy Event")
    date_time = models.DateTimeField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    rsvp_brothers = models.ManyToManyField(Brother)

    def __str__(self):
        return self.name


class ServiceEvent(models.Model):
    name = models.CharField(max_length=200, default="Service Event")
    date_time = models.DateTimeField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    rsvp_brothers = models.ManyToManyField(Brother)

    def __str__(self):
        return self.name


class RecruitmentEvent(models.Model):
    name = models.CharField(max_length=200, default="Recruitment Event")
    date_time = models.DateTimeField()
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    attendees = models.ManyToManyField(PotentialNewMember)

    def __str__(self):
        return self.name


class EventExcuse(models.Model):
    event = models.ForeignKey(ChapterEvent, on_delete=models.CASCADE)
    brother = models.ForeignKey(Brother, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE, null=True)
    description = models.TextField("Reasoning", default="I will not be attending because")
    response_message = models.TextField(default="Your excuse was not approved because")

    STATUS_CHOICES = (
        ('0', 'Pending'),
        ('1', 'Approved'),
        ('2', 'Denied'),
    )

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default='0',
    )

    def __str__(self):
        return self.brother.first_name + " " + self.brother.last_name + "- " + self.event.name
