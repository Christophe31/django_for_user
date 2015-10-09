#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
