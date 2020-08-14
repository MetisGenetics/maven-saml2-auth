#!/usr/bin/env python
# -*- coding:utf-8 -*-
from django.shortcuts import render
logger = getLogger('django-saml2-auth.views')

def denied(r):
    """
    Helper function to render the denied template
    """
    return render(r, 'django_saml2_auth/denied.html')