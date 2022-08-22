from django.urls import re_path
from . import views, maven, tch

app_name = 'django_saml2_auth'

urlpatterns = [
    re_path(r'^maven_acs/$', maven.acs, name="maven_acs"),
    re_path(r'^tch_acs/$', tch.acs, name="tch_acs"),
    re_path(r'^denied/$', views.denied, name="denied"),
]
