#! /usr/bin/env python
# -*- coding: utf-8 -*-
import django_for_user as for_user
from django.db import models
from django.db.models import Q
from django.conf import settings
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Client(models.Model):
    name = models.CharField(max_length=100)
    objects = for_user.ForUserManager()

    @classmethod
    def for_user(cls, user, **kwargs):
        return Q(region__group__users=user)

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Region(models.Model):
    name = models.CharField(max_length=100)
    client = models.ForeignKey(Client)
    objects = for_user.ForUserManager()

    @classmethod
    def for_user(cls, user, **kwargs):
        if user.has_perm("app.see_client_regions"):
            return Q(client__region__group__users=user)
        return Q(group__users=user)

    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL)
    objects = for_user.ForUserManager()

    @classmethod
    def for_user(cls, user, **kwargs):
        if user.has_perm("app.see_all_groups"):
            return Q()
        return Q(users=user)

    def __str__(self):
        return self.name

Group = python_2_unicode_compatible(Group)
