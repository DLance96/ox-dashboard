from django.conf.urls import url
from . import views

app_name = 'dashboard'

urlpatterns = [
    url(r'^$', views.home, name="home"),
    url(r'^brother/', views.brother_view, name="brother"),
    url(r'^president/', views.president, name="president"),
    url(r'^vice-president/', views.v_president, name="v_president"),
    url(r'^treasurer/', views.treasurer, name="treasurer"),
    url(r'^secretary/$', views.secretary, name="secretary"),
    url(r'^secretary/event/add/$', views.secretary_add_event, name="secretary_add_event"),
    url(r'^secretary/event/(?P<event_id>[0-9]+)/$', views.secretary_event, name="secretary_event"),
    url(r'^secretary/excuse/(?P<excuse_id>[0-9]+)/$', views.secretary_excuse, name="secretary_excuse"),
    url(r'^recruitment-chair/', views.recruitment_c, name="recruitment_c"),
    url(r'^scholarship-chair/', views.scholarship_c, name="scholarship_c"),
    url(r'^service-chair/', views.service_c, name="service_c"),
    url(r'^philanthropy-chair/', views.philanthropy_c, name="philanthropy_c"),
    url(r'^detail-manager/', views.detail_m, name="detail_m"),
]