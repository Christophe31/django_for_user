.. image:: https://travis-ci.org/Christophe31/django_for_user.svg?branch=master
    :target: https://travis-ci.org/Christophe31/django_for_user

What is this?
=============

This is a library which will allow you to add a `for_user` method to your
model's querysets and restrict access by users to any entries from the database.

This allow a fine line by line access permission but does not provide much
access context by default. It's permission to see / list items, it does
not tell what you can do with them.


Warning/Welcome Message
=======================

Hi I published this light version of an internal project code because
I find this tool provides something should be a base feature of django.

Let me know if you use this tool or want an improvement in it… For now,
I simply publish it so you can play with it and give some feedback if
you find this interresting.

I'm French and you'll see typos and gramatical non-senses, in this
description, in comments or anywhere else, once again, feedback is welcome.

Consider that if I get no feedbacks at all, this project is dead-born as
I use a different version in my main project with some project related internal things.

What features does it provides?
===============================

This project is made to set security filtering at model level once and for all to avoid some security issues.

The main argument is the django user but it's easy to use this code base to filter by django.contrib.site,
session's variable or anything else too thanks to the kwargs of the for_user class method.

Here the main use-cases:

- models
    + Requirements:
        * you need to know how Q objects works:
          `https://docs.djangoproject.com/en/1.8/topics/db/queries/#complex-lookups-with-q`
        * you have to define a class method `for_user` on models
          you want to be filtered.
        * you will have to use or subclass ForUserManager
    + Features:
        * it will allow you to do MyModel.objects.for_user(user) to get
          a queryset of what user can access.
        * superuser can still see everything.
- forms
    + Requirements:
        * you will set as first inheritant of your form the
          `ForUserFormMixin`
        * you must pass request as first argument when you create your form.
    + Features:
        * It will filter all related fields (select…)
        * It will include current selected values even if current
          user should not see it to avoid changes due to right restrictions.
- admin
    * you will set as first inheritant of your ModelAdmin the ForUserAdminMixIn.
    * It will filter your list querysets, your selects querysets, your ListFilter querysets.
    * You still want to use django permissions to know what the user is able to do with models he have access to.
- bonus feature
    * Field grouping in selects (admin and forms)

Can I Haz some exemples?
========================

.. code-block:: python

    # Models usage exemple:

    #! /usr/bin/env python
    # -*- coding: utf-8 -*-
    import django_for_user as for_user
    from django.db import models
    from django.db.models import Q
    from django.conf import settings

    class Client(models.Model):
        name = models.CharField(max_length=100)
        objects = for_user.ForUserManager()

        @classmethod
        def for_user(cls, user, **kwargs):
            return Q(region__group__users=user)

        def __str__(self):
            return self.name

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


    # form exemple
    import django_for_user as for_user
    from django import forms
    from . import models

    class RegionForm(for_user.ForUserFormMixin, forms.ModelForm):
        class Meta:
            model = models.Region

    class GroupForm(for_user.ForUserFormMixin, forms.ModelForm):

        # fields grouping is a bonus feature, it will use optgroup in selects
        fields_grouping = {
            # for the field region, I order by region name and group region by client
            "region": (("name",), "client"),
        }
        class Meta:
            model = models.Group


    # admin exemple
    import django_for_user as for_user
    from django.contrib import admin
    from . import models

    # use admin as usual, just add the mixin (also on inlines)
    class ForUserAdmin(for_user.ForUserAdminMixin, admin.ModelAdmin):
        pass

    admin.site.register(models.Group, ForUserAdmin)
    admin.site.register(models.Region, ForUserAdmin)
    admin.site.register(models.Client, ForUserAdmin)


What is the test coverage?
==========================

I never did TDD, as the first project I ever do with tests, contributions are welcome.

Which License is used?
======================

BSD License, Like Django.

Is there any ugly hack I should know about?
===========================================

I mokey patch Q objects ``__repr__`` method to ease debug.

I change default admin filter for related objects to remove those doing
empty lists and remove entries the user have no right to see.
