=====================================
Django SAML2 Authentication Made Easy
=====================================

:Author: Dylan Gonzales
:Version: Use 1.1.4 for Django <=1.9, 2.2.1 for Django >= 1.9, Latest supported django version is 2.1

.. image:: https://img.shields.io/pypi/pyversions/django-saml2-auth.svg
    :target: https://pypi.python.org/pypi/django-saml2-auth

.. image:: https://img.shields.io/pypi/v/django-saml2-auth.svg
    :target: https://pypi.python.org/pypi/django-saml2-auth

.. image:: https://img.shields.io/pypi/dm/django-saml2-auth.svg
        :target: https://pypi.python.org/pypi/django-saml2-auth

This project is a custom configuration of Fang Li's django-saml2-auth.  It aims to 
leverage some of the best practices and code existing in django-saml2-auth, while allowing
it to work properly for a specific application and client (not an admin user and must implement client via Azure Active Directory)

If you wish to see the original supported package navigate to the master branch or visit https://github.com/fangli/django-saml2-auth


Dependencies
============
This plugin is compatible with Django 1.6/1.7/1.8/1.9/1.10. The `pysaml2` Python
module is required.


Install
=======
This plugin is installed in the requirements.txt file as:
.. code-block:: bash

    # https://github.com/dgonzo27/django-saml2-auth/archive/tch.zip

xmlsec is also required by pysaml2 and is implemented in the Dockerfile:
.. code-block:: bash
    # RUN apt-get install -y xmlsec1


What does this plugin do?
=========================
This plugin allows the developer to configure a login page for a specific client
and redirect the user to a SAML2 SSO authentication service.  Once the user is 
logged in, completes Multi-Factor Authentication, and redirected back to the web application, 
the plugin will check if the user is already in the system.  If not, the user will be 
created using Django's default UserModel, and then assigned to a new Lead Creator instance 
within Maven for the specific organization.  If the user is in the system, the user will be 
authenticated and redirected to their dashboard in Maven.

How to use?
===========
#. Import the views module in your root urls.py

    .. code-block:: python

        import django_saml2_auth.views

#. Override the default login page in the root urls.py file, by adding these
   lines **BEFORE** any `urlpatterns`:

    .. code-block:: python

        # These are the SAML2 related URLs. You can change "^saml2_auth/" regex to
        # any path you want, like "^sso_auth/", "^sso_login/", etc. (required)
        url(r'^saml2_auth/', include('django_saml2_auth.urls')),

        # The following line will create an organization specific login with SAML2 (optional)
        # If you want to specify the after-login-redirect-URL, use parameter "?next=/the/path/you/want"
        # with this view.  Otherwise, implement in the settings seen later or default to the lead creator dashboard.
        url(r'^tch/login/$', django_saml2_auth.views.signin),

        # The following line will replace the admin login with SAML2 (optional)
        # If you want to specify the after-login-redirect-URL, use parameter "?next=/the/path/you/want"
        # with this view.  Otherwise, implement in the settings seen later or default to the lead creator dashboard.
        url(r'^admin/login/$', django_saml2_auth.views.signin),

#. Add 'django_saml2_auth' to INSTALLED_APPS

    .. code-block:: python

        INSTALLED_APPS = [
            '...',
            'django_saml2_auth',
        ]

#. In settings.py, add the SAML2 related configuration.

    # To configure for other organizations or services, you can create a new SAML2_AUTH_ORG 
    # variable and update this repositories django_saml2_auth/views.py to evaluate that configuration 
    # where applicable/desired
    

    .. code-block:: python

        SAML2_AUTH = {
            # Metadata is required, choose either remote url or local file path
            'METADATA_AUTO_CONF_URL': '[The auto(dynamic) metadata configuration URL of SAML2]',
            'METADATA_LOCAL_FILE_PATH': '[The metadata configuration file path]',

            # Optional settings below
            'DEFAULT_NEXT_URL': '/rfr/dashboard',  # Custom target redirect URL after the user get logged in. Must exist in metis/build_assets/js/reverse.js. This setting will be overwritten if you have parameter ?next= specificed in the login URL.
            'CREATE_USER': 'TRUE', # Create a new Django user when a new user logs in. Defaults to True.
            'NEW_USER_PROFILE': {
                'ACTIVE_STATUS': True,  # The default active status for new users
                'STAFF_STATUS': True,  # The staff status for new users
                'SUPERUSER_STATUS': False,  # The superuser status for new users
            },
            'ATTRIBUTES_MAP': {  # Change Email/UserName/FirstName/LastName to corresponding SAML2 userprofile attributes.
                'email': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
                'username': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress',
                'first_name': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname',
                'last_name': 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname',
            },
            'ASSERTION_URL': 'https://mysite.com', # Custom URL to validate incoming SAML requests against
            'ENTITY_ID': 'https://mysite.com/saml2_auth/acs/', # Populates the Issuer element in authn request
            'NAME_ID_FORMAT': FormatString, # Sets the Format property of authn NameIDPolicy element
            'USE_JWT': False, # Set this to True if you are running a Single Page Application (SPA) with Django Rest Framework (DRF), and are using JWT authentication to authorize client users
            'FRONTEND_URL': 'https://myfrontendclient.com', # Redirect URL for the client if you are using JWT auth with DRF. See explanation below
        }

#. In your SAML2 SSO identity provider, set the Single-sign-on URL and Audience
   URI(SP Entity ID) to http://your-domain/saml2_auth/acs/


Explanation
-----------

**METADATA_AUTO_CONF_URL** Auto SAML2 metadata configuration URL

**METADATA_LOCAL_FILE_PATH** SAML2 metadata configuration file path

**CREATE_USER** Determines if a new Django user should be created for new users.

**NEW_USER_PROFILE** Default settings for newly created users

**ATTRIBUTES_MAP** Mapping of Django user attributes to SAML2 user attributes

**ASSERTION_URL** A URL to validate incoming SAML responses against. By default,
django-saml2-auth will validate the SAML response's Service Provider address
against the actual HTTP request's host and scheme. If this value is set, it
will validate against ASSERTION_URL instead - perfect for when django running
behind a reverse proxy.

**ENTITY_ID** The optional entity ID string to be passed in the 'Issuer' element of authn request, if required by the IDP.

**NAME_ID_FORMAT** Set to the string 'None', to exclude sending the 'Format' property of the 'NameIDPolicy' element in authn requests.
Default value if not specified is 'urn:oasis:names:tc:SAML:2.0:nameid-format:transient'.

**USE_JWT** Set this to the boolean True if you are using Django Rest Framework with JWT authentication

**FRONTEND_URL** If USE_JWT is True, you should set the URL of where your frontend is located (will default to DEFAULT_NEXT_URL if you fail to do so). Once the client is authenticated through the SAML/SSO, your client is redirected to the FRONTEND_URL with the user id (uid) and JWT token (token) as query parameters.
Example: 'https://myfrontendclient.com/?uid=<user id>&token=<jwt token>'
With these params your client can now authenticate will server resources.