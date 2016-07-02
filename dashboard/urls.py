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
    url(r'^brother/c-event/(?P<event_id>[0-9]+)/$', views.brother_chapter_event, name="brother_chapter_event"),
    url(r'^brother/r-event/(?P<event_id>[0-9]+)/$', views.brother_recruitment_event, name="brother_recruitment_event"),
    url(r'^brother/excuse/(?P<excuse_id>[0-9]+)/$', views.brother_excuse, name="brother_excuse"),
    url(r'^brother/excuse/(?P<excuse_id>[0-9]+)/edit/$', views.brother_excuse_edit, name="brother_excuse_edit"),
    url(r'^brother/pnm/(?P<pnm_id>[0-9]+)/$', views.brother_pnm, name="brother_pnm"),

    url(r'^president/', views.president, name="president"),
    url(r'^vice-president/', views.vice_president, name="vice_president"),
    url(r'^treasurer/', views.treasurer, name="treasurer"),

    # Secretary URL section
    url(r'^secretary/$', views.secretary, name="secretary"),
    url(r'^secretary/brother/list/$', views.secretary_brother_list, name="secretary_brother_list"),
    url(r'^secretary/brother/(?P<event_id>[0-9]+)/$', views.secretary_brother_view, name="secretary_brother_view"),
    url(r'^secretary/brother/(?P<event_id>[0-9]+)/edit/$', views.secretary_brother_edit, name="secretary_brother_edit"),
    url(r'^secretary/event/add/$', views.secretary_add_event, name="secretary_add_event"),
    url(r'^secretary/event/all/$', views.secretary_all_events, name="secretary_all_event"),
    url(r'^secretary/event/(?P<event_id>[0-9]+)/view/$', views.secretary_view_event, name="secretary_view_event"),
    url(r'^secretary/event/(?P<event_id>[0-9]+)/$', views.secretary_event, name="secretary_event"),
    url(r'^secretary/excuse/(?P<excuse_id>[0-9]+)/$', views.secretary_excuse, name="secretary_excuse"),

    # Marshall URL section
    url(r'^marshall/$', views.marshall, name="marshall"),

    # Recruitment Chair URL sectiion
    url(r'^recruitment-chair/$', views.recruitment_c, name="recruitment_c"),
    url(r'^recruitment-chair/event/(?P<event_id>[0-9]+)/$', views.recruitment_c_event, name="recruitment_c_event"),
    url(r'^recruitment-chair/event/add/$', views.recruitment_c_add_event, name="recruitment_c_add_event"),
    url(r'^recruitment-chair/event/(?P<event_id>[0-9]+)/edit/$', views.recruitment_c_edit_event,
        name="recruitment_c_edit_event"),
    url(r'^recruitment-chair/pnm/(?P<pnm_id>[0-9]+)/$', views.recruitment_c_pnm, name="recruitment_c_pnm"),
    url(r'^recruitment-chair/pnm/(?P<pnm_id>[0-9]+)/edit/$', views.recruitment_c_edit_pnm,
        name="recruitment_c_edit_pnm"),
    url(r'^recruitment-chair/pnm/add/$', views.recruitment_c_add_pnm, name="recruitment_c_add_pnm"),
    url(r'^recruitment-chair/pnm/(?P<pk>\d+)/delete/$', views.PnmDelete.as_view(),
        name="recruitment_c_delete_pnm"),

    url(r'^scholarship-chair/$', views.scholarship_c, name="scholarship_c"),
    url(r'^service-chair/$', views.service_c, name="service_c"),
    url(r'^philanthropy-chair/$', views.philanthropy_c, name="philanthropy_c"),
    url(r'^detail-manager/$', views.detail_m, name="detail_m"),
]
