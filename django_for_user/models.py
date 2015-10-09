#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class ForUserQuerySet(models.QuerySet):
    def for_user(self, user, **kwargs):
        if user.is_superuser:
            return self
        query_filter = self.model.for_user(user, qs=self, **kwargs)
        return self.filter(query_filter).distinct()


class ForUserManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        return ForUserQuerySet(self.model, using=self._db)

    def for_user(self, user, **kwargs):
        return self.get_queryset().for_user(user, **kwargs)
