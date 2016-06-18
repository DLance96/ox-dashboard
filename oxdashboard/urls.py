"""oxdashboard URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$', 'dashboard.views.home', name="home"),
    url(r'^president/', 'dashboard.views.president', name="president"),
    url(r'^vice-president/', 'dashboard.views.v_president', name="v_president"),
    url(r'^treasurer/', 'dashboard.views.treasurer', name="treasurer"),
    url(r'^secretary/', 'dashboard.views.secretary', name="secretary"),
    url(r'^recruitment-chair/', 'dashboard.views.recruitment_c', name="recruitment_c"),
    url(r'^scholarship-chair/', 'dashboard.views.scholarship_c', name="scholarship_c"),
    url(r'^service-chair/', 'dashboard.views.service_c', name="service_c"),
    url(r'^philanthropy-chair/', 'dashboard.views.philanthropy_c', name="philanthropy_c"),
    url(r'^detail-manager/', 'dashboard.views.detail_m', name="detail_m"),
    url(r'^admin/', include(admin.site.urls)),
]
