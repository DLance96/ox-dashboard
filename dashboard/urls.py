from django.conf.urls import url
from . import views

app_name = 'dashboard'

urlpatterns = [

    # login views
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),

    url(r'^$', views.home, name="home"),

    # Brother URL section
    url(r'^brother/$', views.brother_view, name="brother"),
    url(r'^brother/(?P<pk>\d+)/edit/$', views.BrotherEdit.as_view(), name="brother_edit"),
    url(r'^brother/c-event/(?P<event_id>[0-9]+)/$', views.brother_chapter_event, name="brother_chapter_event"),
    url(r'^brother/r-event/(?P<event_id>[0-9]+)/$', views.brother_recruitment_event, name="brother_recruitment_event"),
    url(r'^brother/s-event/(?P<event_id>[0-9]+)/$', views.brother_service_event, name="brother_service_event"),
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
    url(r'^vice-president/', views.vice_president, name="vice_president"),
    url(r'^treasurer/', views.treasurer, name="treasurer"),

    # Secretary URL section
    url(r'^secretary/$', views.secretary, name="secretary"),
    url(r'^secretary/brother/list/$', views.secretary_brother_list, name="secretary_brother_list"),
    url(r'^secretary/brother/(?P<event_id>[0-9]+)/$', views.secretary_brother_view, name="secretary_brother_view"),
    url(r'^secretary/brother/(?P<event_id>[0-9]+)/edit/$', views.secretary_brother_edit, name="secretary_brother_edit"),
    url(r'^secretary/event/add/$', views.secretary_event_add, name="secretary_event_add"),
    url(r'^secretary/event/all/$', views.secretary_all_events, name="secretary_event_all"),
    url(r'^secretary/event/(?P<pk>\d+)/delete/$', views.ChapterEventDelete.as_view(), name="secretary_event_delete"),
    url(r'^secretary/event/(?P<event_id>[0-9]+)/view/$', views.secretary_event_view, name="secretary_event_view"),
    url(r'^secretary/event/(?P<event_id>[0-9]+)/$', views.secretary_event, name="secretary_event"),
    url(r'^secretary/excuse/(?P<excuse_id>[0-9]+)/$', views.secretary_excuse, name="secretary_excuse"),

    # Marshall URL section
    url(r'^marshall/$', views.marshall, name="marshall"),

    # Recruitment Chair URL section
    url(r'^recruitment-chair/$', views.recruitment_c, name="recruitment_c"),
    url(r'^recruitment-chair/event/(?P<event_id>[0-9]+)/$', views.recruitment_c_event, name="recruitment_c_event"),
    url(r'^recruitment-chair/event/add/$', views.recruitment_c_event_add, name="recruitment_c_event_add"),
    url(r'^recruitment-chair/event/(?P<event_id>[0-9]+)/edit/$', views.recruitment_c_event_edit,
        name="recruitment_c_event_edit"),
    url(r'^recruitment-chair/event/(?P<pk>\d+)/delete/$', views.RecruitmentEventDelete.as_view(),
        name="recruitment_c_event_delete"),
    url(r'^recruitment-chair/pnm/(?P<pnm_id>[0-9]+)/$', views.recruitment_c_pnm, name="recruitment_c_pnm"),
    url(r'^recruitment-chair/pnm/(?P<pk>\d+)/edit/$', views.PnmEdit.as_view(),
        name="recruitment_c_pnm_edit"),
    url(r'^recruitment-chair/pnm/add/$', views.recruitment_c_pnm_add, name="recruitment_c_pnm_add"),
    url(r'^recruitment-chair/pnm/(?P<pk>\d+)/delete/$', views.PnmDelete.as_view(),
        name="recruitment_c_pnm_delete"),

    url(r'^scholarship-chair/$', views.scholarship_c, name="scholarship_c"),
    url(r'^service-chair/$', views.service_c, name="service_c"),
    url(r'^service-chair/(?P<pk>\d+)/response/$', views.ServiceSubmissionChairEdit.as_view(),
        name="service_c_submission_response"),
    url(r'^service-chair/event/(?P<event_id>[0-9]+)/$', views.service_c_event,
        name="service_c_event"),
    url(r'^service-chair/event/add/$', views.service_c_event_add, name="service_c_event_add"),
    url(r'^service-chair/event/(?P<pk>\d+)/delete/$', views.ServiceEventDelete.as_view(),
        name="service_c_event_delete"),

    url(r'^philanthropy-chair/$', views.philanthropy_c, name="philanthropy_c"),
    url(r'^detail-manager/$', views.detail_m, name="detail_m"),
]
