#!/usr/bin/env python
# -*- coding: utf-8 -*-
import django_for_user as for_user
from django.contrib import admin
from . import models

# use admin as usual, just add the mixin (also on inlines)
class ForUserAdmin(for_user.ForUserAdminMixin, admin.ModelAdmin):
    pass

admin.site.register(models.Group, ForUserAdmin)
admin.site.register(models.Region, ForUserAdmin)
admin.site.register(models.Client, ForUserAdmin)
