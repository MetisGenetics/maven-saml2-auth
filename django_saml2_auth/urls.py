from django.conf.urls import url
from . import views, maven, tch

app_name = 'django_saml2_auth'

urlpatterns = [
    url(r'^maven_acs/$', maven.acs, name="maven_acs"),
    url(r'^tch_acs/$', tch.acs, name="tch_acs"),
    url(r'^denied/$', views.denied, name="denied"),
]