#!/usr/bin/env python
# -*- coding:utf-8 -*-
from saml2 import (BINDING_HTTP_POST, BINDING_HTTP_REDIRECT, entity)
from saml2.client import Saml2Client
from saml2.config import Config as Saml2Config
from django import get_version
from pkg_resources import parse_version
from django.conf import settings
from django.contrib.auth import login, logout, get_user_model
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import is_safe_url
from logging import getLogger

logger = getLogger('django-saml2-auth.maven')
User = get_user_model() # Default user

# Get imports based on installed versions
try:
    import urllib2 as _urllib
except:
    import urllib.request as _urllib
    import urllib.error
    import urllib.parse

if parse_version(get_version()) >= parse_version('1.7'):
    from django.utils.module_loading import import_string
else:
    from django.utils.module_loading import import_by_path as import_string


def default_next_url():
    """
    Helper function to obtain the default next url in the SAML2 Schema
    """
    logger.debug('maven.default_next_url')
    if 'DEFAULT_NEXT_URL' in settings.MAVEN_SAML2_AUTH:
        return settings.MAVEN_SAML2_AUTH['DEFAULT_NEXT_URL']
    else:
        return reverse('start_page')


def get_reverse(objects):
    """
    Helper function to call reverse() on a list of objects
    """
    logger.debug('maven.get_reverse')
    if parse_version(get_version()) >= parse_version('2.0'):
        from django.urls import reverse
    else:
        from django.core.urlresolvers import reverse
    if objects.__class__.__name__ not in ['list', 'tuple']:
        objects = [objects]

    for obj in objects:
        try:
            return reverse(obj)
        except:
            pass
    raise Exception('URL reverse issue %s. Known issue from fangli/django-saml2-auth' % str(objects))


def get_current_domain(r):
    """
    Helper function to obtain the current domain (assertion url) 
    from the SAML2 Schema
    """
    logger.debug('maven.get_current_domain')
    if 'ASSERTION_URL' in settings.MAVEN_SAML2_AUTH:
        return settings.MAVEN_SAML2_AUTH['ASSERTION_URL']
    return '{scheme}://{host}'.format(scheme='https' if r.is_secure() else 'http', host=r.get_host())


def get_metadata():
    """
    Helper function to obtain the metadata in the SAML2 Schema
    """
    logger.debug('maven.get_metadata')
    if 'METADATA_LOCAL_FILE_PATH' in settings.MAVEN_SAML2_AUTH:
        return {
            'local': [settings.MAVEN_SAML2_AUTH['METADATA_LOCAL_FILE_PATH']]
        }
    else:
        return {
            'remote': [
                {
                    'url': settings.MAVEN_SAML2_AUTH['METADATA_AUTO_CONF_URL'],
                },
            ]
        }


def get_saml_client(domain):
    """
    Helper function to obtain the SAML2 client given the domain
    """
    logger.debug('maven.get_saml_client')
    acs_url = domain + get_reverse([acs, 'maven_acs', 'django_saml2_auth:maven_acs'])
    metadata = get_metadata()
    
    saml_settings = {
        'metadata': metadata,
        'service': {
            'sp': {
                'endpoints': {
                    'assertion_consumer_service': [
                        (acs_url, BINDING_HTTP_REDIRECT),
                        (acs_url, BINDING_HTTP_POST)
                    ],
                },
                'allow_unsolicited': True,
                'authn_requests_signed': False,
                'logout_requests_signed': True,
                'want_assertions_signed': True,
                'want_response_signed': False,
            },
        },
    }

    if 'ENTITY_ID' in settings.MAVEN_SAML2_AUTH:
        saml_settings['entityid'] = settings.MAVEN_SAML2_AUTH['ENTITY_ID']

    spConfig = Saml2Config()
    spConfig.load(saml_settings)
    spConfig.allow_unknown_attributes = True
    saml_client = Saml2Client(config=spConfig)
    return saml_client


@csrf_exempt
def acs(r):
    """
    View function to handle logic after SSO user login
    """
    logger.debug('maven.acs')
    saml_client = get_saml_client(get_current_domain(r))
    response = r.POST.get('SAMLResponse', None)
    next_url = r.session.get('login_next_url', settings.MAVEN_SAML2_AUTH.get('DEFAULT_NEXT_URL', '/bok/$'))
    
    if not response:
        return HttpResponseRedirect(reverse('denied'))
    
    authn_response = saml_client.parse_authn_request_response(response, entity.BINDING_HTTP_POST)
    if authn_response is None:
        return HttpResponseRedirect(reverse('denied'))

    user_identity = authn_response.get_identity()
    if user_identity is None:
        return HttpResponseRedirect(reverse('denied'))

    # For Google Cloud Directory Mapping
    user_email = user_identity[settings.MAVEN_SAML2_AUTH.get('ATTRIBUTES_MAP', {}).get('email', 'email')][0]
    target_user = None

    # Try to query the user by username (user_email)
    try:
        target_user = User.objects.get(username=user_email)
    # If the user DNE, return the denied page
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('denied'))

    # If the user is active, we want to login
    if target_user.is_active:
        logger.debug('trying to authenticate')
        target_user.backend = 'refer.utils.EmailBackEnd'
        login(r, target_user)
        return redirect(reverse('start_page'))
    else:
        return HttpResponseRedirect(reverse('denied'))


def signin(r):
    """
    Helper function to redirect to client default SSO login
    """
    logger.debug('maven.signin')
    try:
        import urlparse as _urlparse
        from urllib import unquote
    except:
        import urllib.parse as _urlparse
        from urllib.parse import unquote

    next_url = r.GET.get('next', default_next_url())

    try:
        if 'next=' in unquote(next_url):
            next_url = _urlparse.parse_qs(_urlparse.urlparse(unquote(next_url)).query)['next'][0]
    except:
        next_url = r.GET.get('next', default_next_url())

    # Only permit signin requests where the next url is a safe url
    if parse_version(get_version()) >= parse_version('2.0'):
        url_ok = is_safe_url(next_url, None)
    else:
        url_ok = is_safe_url(next_url)

    if not url_ok:
        return HttpResponseRedirect(reverse('denied'))

    r.session['login_next_url'] = next_url

    saml_client = get_saml_client(get_current_domain(r))
    _, info = saml_client.prepare_for_authenticate()
    redirect_url = None

    for key, value in info['headers']:
        if key == 'Location':
            redirect_url = value
            break

    return HttpResponseRedirect(redirect_url)


def signout(r):
    """
    Helper function to render a custom signout template
    """
    logger.debug('maven.signout')
    logout(r)
    return render(r, 'django_saml2_auth/signout.html')