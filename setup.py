"""
The setup module for django_saml2_auth.
See: https://github.com/MetisGenetics/django-saml2-auth
"""

from codecs import open
from setuptools import (setup, find_packages)
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django_saml2_auth',
    version='3.0.0',
    description='SAML2 Authentication for Genetics Maven. Easily integrate with SAML2 SSO identity providers like Google Cloud Directory, Azure Active Directory and more',
    long_description=long_description,
    url='https://github.com/MetisGenetics/maven-saml2-auth',
    author='Dylan Gonzales',
    author_email='dylan.gonzales@metisgenetics.com',
    license='MIT',
    classifiers=[
        #   3 - Alpha, 4 - Beta, 5 - Production/Stable
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: MIT Approved :: The MIT License (MIT)',
        'Framework :: Django :: 3.0.8',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='Maven SAML2 Authentication',
    packages=find_packages(),
    install_requires=[
        'pysaml2>=4.5.0',
        'djangorestframework-jwt',
        'django-rest-auth', 
    ],
    include_package_data=True,
)