#!/usr/bin/env python
from setuptools import setup

setup(
    name='django-for-user',
    version='0.0.1',
    description="Django for_user filter models rows by users in forms and admin.",
    author="Christophe Narbonne",
    author_email='@Christophe31',
    url='https://github.com/Christophe31/django-for-user',
    packages=['django_for_user'],
    license='BSD',
    long_description=open('README.rst').read(),
)
