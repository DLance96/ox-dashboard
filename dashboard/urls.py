from django.conf.urls import url

from . import views

app_name = 'dashboard'

urlpatterns = [

    # login views
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^brother/change-password/$', views.change_password, name="change_password"),

    url(r'^$', views.home, name="home"),

    # General Info
    url(r'^general/brother-info-list/$', views.brother_info_list, name="brother_info_list"),
    url(r'^general/contact-list/$', views.contact_list, name="contact_list"),
    url(r'^general/emergency-contact-list/$', views.emergency_contact_list, name="emergency_contact_list"),
    url(r'^general/event-list/$', views.event_list, name="event_list"),

    # Brother URL section
    url(r'^brother/$', views.brother_view, name="brother"),
    url(r'^brother/(?P<pk>\d+)/edit/$', views.BrotherEdit.as_view(), name="brother_edit"),
    url(r'^brother/c-event/(?P<event_id>[0-9]+)/$', views.brother_chapter_event, name="brother_chapter_event"),
    url(r'^brother/r-event/(?P<event_id>[0-9]+)/$', views.brother_recruitment_event, name="brother_recruitment_event"),
    url(r'^brother/s-event/(?P<event_id>[0-9]+)/$', views.brother_service_event, name="brother_service_event"),
    url(r'^brother/p-event/(?P<event_id>[0-9]+)/$', views.brother_philanthropy_event,
        name="brother_philanthropy_event"),
    url(r'^brother/excuse/(?P<excuse_id>[0-9]+)/$', views.brother_excuse, name="brother_excuse"),
    url(r'^brother/excuse/(?P<pk>\d+)/delete/$', views.ExcuseDelete.as_view(), name="brother_excuse_delete"),
    url(r'^brother/excuse/(?P<pk>\d+)/$', views.ExcuseEdit.as_view(), name="brother_excuse_edit"),
    url(r'^brother/service-submission/(?P<submission_id>[0-9]+)/$', views.brother_service_submission,
        name="brother_service_submission"),
    url(r'^brother/service-submission/(?P<pk>\d+)/edit/$', views.ServiceSubmissionEdit.as_view(),
        name="brother_service_submission_edit"),
    url(r'^brother/service-submission/(?P<pk>\d+)/delete/$', views.ServiceSubmissionDelete.as_view(),
        name="brother_service_submission_delete"),
    url(r'^brother/service-submission/add/$', views.brother_service_submission_add,
        name="brother_service_submission_add"),
    url(r'^brother/pnm/(?P<pnm_id>[0-9]+)/$', views.brother_pnm, name="brother_pnm"),

    url(r'^president/', views.president, name="president"),

    # Vice President URL Section
    url(r'^vice-president/$', views.vice_president, name="vice_president"),
    url(r'^vice-president/committee-meeting/add/$', views.vice_president_committee_meeting_add,
        name="vice_president_committee_meeting_add"),
    url(r'^vice-president/committee-meeting/(?P<pk>\d+)/edit/$', views.CommitteeMeetingEdit.as_view(),
        name="vice_president_committee_meeting_edit"),
    url(r'^vice-president/committee-meeting/(?P<pk>\d+)/delete/$', views.CommitteeMeetingDelete.as_view(),
        name="vice_president_committee_meeting_delete"),

    url(r'^treasurer/', views.treasurer, name="treasurer"),

    # Secretary URL section
    url(r'^secretary/$', views.secretary, name="secretary"),
    url(r'^secretary/positions/$', views.secretary_positions, name="secretary_positions"),
    url(r'^secretary/positions/add/$', views.secretary_position_add, name="secretary_position_add"),
    url(r'^secretary/position/(?P<pk>\d+)/edit/$', views.PositionEdit.as_view(), name="secretary_position_edit"),
    url(r'^secretary/position/(?P<pk>\d+)/delete/$', views.PositionDelete.as_view(), name="secretary_position_delete"),
    url(r'^secretary/attendance/$', views.secretary_attendance, name="secretary_attendance"),
    url(r'^secretary/brother/list/$', views.secretary_brother_list, name="secretary_brother_list"),
    url(r'^secretary/brother/(?P<brother_id>[0-9]+)/$', views.secretary_brother_view, name="secretary_brother_view"),
    url(r'^secretary/brother/(?P<pk>\d+)/edit/$', views.SecretaryBrotherEdit.as_view(), name="secretary_brother_edit"),
    url(r'^secretary/brother/(?P<pk>\d+)/delete/$', views.SecretaryBrotherDelete.as_view(),
        name="secretary_brother_delete"),
    url(r'^secretary/brother/add/$', views.secretary_brother_add, name="secretary_brother_add"),
    url(r'^secretary/event/add/$', views.secretary_event_add, name="secretary_event_add"),
    url(r'^secretary/event/all/$', views.secretary_all_events, name="secretary_event_all"),
    url(r'^secretary/event/(?P<pk>\d+)/delete/$', views.ChapterEventDelete.as_view(), name="secretary_event_delete"),
    url(r'^secretary/event/(?P<pk>\d+)/edit/$', views.ChapterEventEdit.as_view(), name="secretary_event_edit"),
    url(r'^secretary/event/(?P<event_id>[0-9]+)/view/$', views.secretary_event_view, name="secretary_event_view"),
    url(r'^secretary/event/(?P<event_id>[0-9]+)/$', views.secretary_event, name="secretary_event"),
    url(r'^secretary/excuse/(?P<excuse_id>[0-9]+)/$', views.secretary_excuse, name="secretary_excuse"),
    url(r'^secretary/excuses', views.secretary_all_excuses, name="secretary_excuses"),

    # Marshal URL section
    url(r'^marshal/$', views.marshal, name="marshal"),
    url(r'^marshal/candidate/add/$', views.marshal_candidate_add, name="marshal_candidate_add"),
    url(r'^marshal/candidate/(?P<brother_id>[0-9]+)/$', views.marshal_candidate, name="marshal_candidate"),
    url(r'^marshal/candidate/(?P<pk>\d+)/edit/$', views.CandidateEdit.as_view(), name="marshal_candidate_edit"),
    url(r'^marshal/candidate/(?P<pk>\d+)/delete/$', views.CandidateDelete.as_view(), name="marshal_candidate_delete"),

    # Recruitment Chair URL section
    url(r'^recruitment-chair/$', views.recruitment_c, name="recruitment_c"),
    url(r'^recruitment-chair/rush-attendance/$', views.recruitment_c_rush_attendance,
        name="recruitment_c_rush_attendance"),
    url(r'^recruitment-chair/event/(?P<event_id>[0-9]+)/$', views.recruitment_c_event, name="recruitment_c_event"),
    url(r'^recruitment-chair/event/add/$', views.recruitment_c_event_add, name="recruitment_c_event_add"),
    url(r'^recruitment-chair/event/(?P<pk>\d+)/edit/$', views.RecruitmentEventEdit.as_view(),
        name="recruitment_c_event_edit"),
    url(r'^recruitment-chair/event/(?P<pk>\d+)/delete/$', views.RecruitmentEventDelete.as_view(),
        name="recruitment_c_event_delete"),
    url(r'^recruitment-chair/pnm/(?P<pnm_id>[0-9]+)/$', views.recruitment_c_pnm, name="recruitment_c_pnm"),
    url(r'^recruitment-chair/pnm/(?P<pk>\d+)/edit/$', views.PnmEdit.as_view(),
        name="recruitment_c_pnm_edit"),
    url(r'^recruitment-chair/pnm/add/$', views.recruitment_c_pnm_add, name="recruitment_c_pnm_add"),
    url(r'^recruitment-chair/pnm/(?P<pk>\d+)/delete/$', views.PnmDelete.as_view(), name="recruitment_c_pnm_delete"),

    # Scholarship Chair URL Section
    url(r'^scholarship-chair/$', views.scholarship_c, name="scholarship_c"),
    url(r'^scholarship-chair/gpa/$', views.scholarship_c_gpa, name="scholarship_c_gpa"),
    url(r'^scholarship-chair/event/(?P<event_id>[0-9]+)/$', views.scholarship_c_event, name="scholarship_c_event"),
    url(r'^scholarship-chair/event/add/$', views.scholarship_c_event_add, name="scholarship_c_event_add"),
    url(r'^scholarship-chair/event/(?P<pk>\d+)/edit/$', views.StudyEventEdit.as_view(),
        name="scholarship_c_event_edit"),
    url(r'^scholarship-chair/event/(?P<pk>\d+)/delete/$', views.StudyEventDelete.as_view(),
        name="scholarship_c_event_delete"),
    url(r'^scholarship-chair/plan/(?P<plan_id>[0-9]+)/$', views.scholarship_c_plan, name="scholarship_c_plan"),
    url(r'^scholarship-chair/plan/(?P<pk>\d+)/edit/$', views.ScholarshipReportEdit.as_view(),
        name="scholarship_c_plan_edit"),

    # Service Chair URL section
    url(r'^service-chair/$', views.service_c, name="service_c"),
    url(r'^service-chair/(?P<pk>\d+)/response/$', views.ServiceSubmissionChairEdit.as_view(),
        name="service_c_submission_response"),
    url(r'^service-chair/event/(?P<event_id>[0-9]+)/$', views.service_c_event,
        name="service_c_event"),
    url(r'^service-chair/event/add/$', views.service_c_event_add, name="service_c_event_add"),
    url(r'^service-chair/event/(?P<pk>\d+)/delete/$', views.ServiceEventDelete.as_view(),
        name="service_c_event_delete"),
    url(r'^service-chair/event/(?P<pk>\d+)/edit/$', views.ServiceEventEdit.as_view(),
        name="service_c_event_edit"),
    url(r'^service-chair/hours/$', views.service_c_hours, name='service_c_hours'),

    # Philanthropy Chair URL Section
    url(r'^philanthropy-chair/$', views.philanthropy_c, name="philanthropy_c"),
    url(r'^philanthropy-chair/event/(?P<event_id>[0-9]+)/$', views.philanthropy_c_event,
        name="philanthropy_c_event"),
    url(r'^philanthropy-chair/event/add/$', views.philanthropy_c_event_add, name="philanthropy_c_event_add"),
    url(r'^philanthropy-chair/event/(?P<pk>\d+)/delete/$', views.PhilanthropyEventDelete.as_view(),
        name="philanthropy_c_event_delete"),
    url(r'^philanthropy-chair/event/(?P<pk>\d+)/edit/$', views.PhilanthropyEventEdit.as_view(),
        name="philanthropy_c_event_edit"),

    url(r'^detail-manager/$', views.detail_m, name="detail_m"),
]
