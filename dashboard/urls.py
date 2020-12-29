from django.conf.urls import url
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static


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
    url(r'^general/committee-list/$', views.committee_list,
        name="committee_list"),
    url(r'^general/emergency_phone_tree/$', views.emergency_phone_tree_view, name="emergency_phone_tree_view"),
    url(r'^general/meet-a-brother/$', views.meet_a_brother, name="meet_a_brother"),
    url(r'^general/create-report/$', views.create_report, name="create_report"),
    url(r'^general/report/(?P<pk>\d+)/edit/$', views.EditReport.as_view(), name="edit_report"),
    url(r'^general/report/(?P<pk>\d+)/delete/$', views.DeleteReport.as_view(), name="delete_report"),

    url(r'^classes/$', views.classes, name="classes"),
    url(r'^classes/add/$', views.classes_add, name="classes_add"),
    url(r'^classes/(?P<pk>\d+)/delete/$', views.ClassesDelete.as_view(), name="classes_delete"),
    url(r'^classes/brother=(?P<brother>\d+)/$', views.classes, name="classes"),
    url(r'^classes/department=(?P<department>\D+)/$', views.classes, name="classes"),
    url(r'^classes/class=(?P<number>\d+)/$', views.classes, name="classes"),
    url(r'^classes/department=(?P<department>\D+)/brother=(?P<brother>\d+)/$', views.classes, name="classes"),
    url(r'^classes/number=(?P<number>\d+)/brother-(?P<brother>\d+)/$', views.classes, name="classes"),
    url(r'^classes/department=(?P<department>\D+)/number=(?P<number>\d+)/$', views.classes, name="classes"),
    url(r'^classes/department=(?P<department>\D+)/number=(?P<number>\d+)/brother=(?P<brother>\d+)/$', views.classes, name="classes"),

    url(r'^committee/(?P<pk>\d+)/edit/$', views.CommitteeEdit.as_view(), name="committee_edit"),
    url(r'^committee/(?P<pk>\d+)/delete/$', views.CommitteeDelete.as_view(), name="committee_delete"),
    url(r'^committee/event/(?P<event_id>[0-9]+)/$', views.committee_event, name="committee_event"),
    url(r'^committee/event/(?P<pk>\d+)/edit/$', views.CommitteeEventEdit.as_view(),
        name="committee_event_edit"),
    url(r'^(?P<position>\D+)/committee/event/add/$',
        views.committee_event_add, name="committee_event_add"),
    url(r'^committee/event/(?P<pk>\d+)/delete/$', views.CommitteeEventDelete.as_view(),
        name="committee_event_delete"),

    # Brother URL section
    url(r'^brother/$', views.brother_view, name="brother"),
    url(r'^brother/(?P<pk>\d+)/edit/$', views.BrotherEdit.as_view(), name="brother_edit"),
    url(r'^brother/c-event/(?P<view>\D+)/(?P<event_id>[0-9]+)/$', views.brother_chapter_event, name="brother_chapter_event"),
    url(r'^brother/r-event/(?P<view>\D+)/(?P<event_id>[0-9]+)/$', views.brother_recruitment_event, name="brother_recruitment_event"),
    url(r'^brother/s-event/(?P<view>\D+)/(?P<event_id>[0-9]+)/$', views.brother_service_event, name="brother_service_event"),
    url(r'^brother/hs-event/(?P<view>\D+)/(?P<event_id>[0-9]+)/$', views.brother_hs_event, name="brother_hs_event"),
    url(r'^brother/p-event/(?P<view>\D+)/(?P<event_id>[0-9]+)/$', views.brother_philanthropy_event,
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
    url(r'^brother/media-account/add/$', views.media_account_add, name="media_account_add"),
    url(r'^brother/media-account/(?P<pk>\d+)/delete/$', views.MediaAccountDelete.as_view(), name="media_account_delete"),
    url(r'^brother/media/add/$', views.media_add, name="media_add"),
    url(r'^brother/campus-groups/add/$', views.campus_groups_add, name="campus_groups_add"),
    url(r'^brother/campus-groups/(?P<pk>\d+)/delete/$', views.campus_groups_delete, name="campus_groups_delete"),

    url(r'^president/$', views.president, name="president"),
    url(r'^president/recreate-phone-tree/$', views.create_phone_tree, name="create_phone_tree"),

    # Vice President URL Section
    url(r'^vice-president/$', views.vice_president, name="vice_president"),
    url(r'^vice-president/committee-assignments/$', views.vice_president_committee_assignments,
        name="vice_president_committee_assignments"),
    url(r'^vice_president/in_house', views.in_house, name='vice_president_in_house'),

    # Vice President Health and Safety URL Section
    url(r'^vphs/$', views.vphs, name="vphs"),
    url(r'^vphs/hs_event/add/$', views.health_and_safety_event_add,
        name="health_and_safety_event_add"),
    url(r'^vphs/hs_event/(?P<pk>\d+)/edit/$', views.HealthAndSafetyEdit.as_view(),
        name="health_and_safety_event_edit"),
    url(r'^vphs/hs_event/(?P<pk>\d+)/delete/$', views.HealthAndSafetyDelete.as_view(),
        name="health_and_safety_event_delete"),
    url(r'^vphs/hs_event/(?P<event_id>[0-9]+)/$', views.health_and_safety_event, name="health_safety_event"),

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
    url(r'^secretary/agenda/$', views.secretary_agenda, name="secretary_agenda"),

    # Marshal URL section
    url(r'^marshal/$', views.marshal, name="marshal"),
    url(r'^marshal/candidate/add/$', views.marshal_candidate_add, name="marshal_candidate_add"),
    url(r'^marshal/candidate/(?P<brother_id>[0-9]+)/$', views.marshal_candidate, name="marshal_candidate"),
    url(r'^marshal/candidate/(?P<pk>\d+)/edit/$', views.CandidateEdit.as_view(), name="marshal_candidate_edit"),
    url(r'^marshal/candidate/(?P<pk>\d+)/delete/$', views.CandidateDelete.as_view(), name="marshal_candidate_delete"),
    url(r'^marshal/mab/edit/$', views.marshal_mab_edit, name="marshal_mab_edit"),
    url(r'^marshal/mab/edit/candidate$', views.marshal_mab_edit_candidate, name="marshal_mab_edit_candidate"),

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

    url(r'^recruitment-chair/pnm/all_pnms.csv$', views.all_pnm_csv, name="all_pnm_csv"),

    # Scholarship Chair URL Section
    url(r'^scholarship-chair/$', views.scholarship_c, name="scholarship_c"),
    url(r'^scholarship-chair/gpa/$', views.scholarship_c_gpa, name="scholarship_c_gpa"),
    url(r'^scholarship-chair/event/(?P<event_id>[0-9]+)/$', views.study_table_event, name="scholarship_c_event"),
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
    url(r'^service-chair/(?P<submission_id>[0-9]+)/response/$', views.service_c_submission_response,
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
    url(r'^detail-manager/supplies-request/$', views.supplies_request, name='supplies_request'),
    url(r'^detail-manager/supplies-list/$', views.supplies_list, name='supplies_list'),
    url(r'^detail-manager/supplies-finish/$', views.supplies_finish, name='supplies_finish'),
    url(r'^detail-manager/house-detail-toggle$', views.house_detail_toggle, name='house_detail_toggle'),
    url(r'^detail-manager/create-groups$', views.create_groups, name='create_groups'),
    url(r'^detail-manager/select-groups$', views.select_groups, name='select_groups'),
    url(r'^detail-manager/delete-groups$', views.delete_groups, name='delete_groups'),
    url(r'^detail-manager/all-users-details$', views.all_users_details, name='all_users_details'),
    url(r'^detail-manager/details-by-date$', views.detail_dates, name='details_by_date'),
    url(r'^detail-manager/details-on/(?P<date>.+)/$', views.details_on_date, name='details_on_date'),

    url(r'^details/$', views.current_details, name='list_details'),
    url(r'details/fine/$', views.detail_fines, name='detail_fine'),
    url(r'details/fine/(?P<brother_id>\d+)/$', views.detail_fines_brother, name='detail_fine_brother'),
    url(r'details/all/$', views.all_details, name='all_details'),
    url(r'^details/(?P<brother_id>\d+)/$', views.current_details_brother, name='list_details_brother'),
    url(r'details/all/(?P<brother_id>\d+)/$', views.all_details_brother, name='all_details_brother'),
    url(r'^details/thursday/finish/(?P<detail_id>\d+)/$', views.finish_thursday_detail,
        name='finish_thursday'),
    url(r'details/thursday/post$', views.post_thursday, name='post_thursday_details'),

    url(r'^details/sunday/finish/(?P<detail_id>\d+)/$', views.finish_sunday_detail,
        name='finish_sunday'),
    url(r'details/sunday/post$', views.post_sunday, name='post_sunday_details'),

    url(r'^prchair/$', views.public_relations_c, name="public_relations_c"),
    url(r'^social-chair/$', views.social_c, name="social_c"),
    url(r'^alumni-relations-chair/$', views.alumni_relations_c, name="alumni_relations_c"),
    url(r'^memdev-chair/$', views.memdev_c, name="memdev_c"),

    # Connect with Us URL section
    url(r'^minecraft/$', views.minecraft, name ='minecraft'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    url(r'^(?P<path>.*\..*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]
