#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models.fields.related import ForeignObjectRel
from django.contrib.admin.options import BaseModelAdmin
from django.contrib.admin import (
    RelatedFieldListFilter, FieldListFilter,)
from django.contrib.admin.utils import get_model_from_relation
from django.utils.encoding import smart_text

from .forms import ForUserBaseMixin


########################
# Admin mixins and tools
########################
class ForUserRelatedListFilter(RelatedFieldListFilter):
    def field_choices(self, field, request, model_admin):
        other_model = get_model_from_relation(field)
        qs = other_model.objects.exclude(**{field.related_query_name(): None})
        if isinstance(model_admin, ForUserAdminMixin):
            if hasattr(qs, 'for_user'):
                qs = qs.for_user(request.user)
        return [(x._get_pk_val(), smart_text(x)) for x in qs]


FieldListFilter.register(lambda f: (
    bool(f.rel) if hasattr(f, 'rel') else
    isinstance(f, ForeignObjectRel)),
    ForUserRelatedListFilter, take_priority=True)


class ForUserAdminMixin(ForUserBaseMixin, BaseModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(ForUserAdminMixin, self).get_form(request, obj, **kwargs)
        self.filter_form(form, request, obj)
        return form

    def get_formset(self, request, obj=None, **kwargs):
        formset = super(ForUserAdminMixin, self).get_formset(request, obj, **kwargs)
        self.filter_form(formset.form, request, obj)
        return formset

    def field_filter_local(self, name, field):
        pass

    def get_queryset(self, request):
        qs = super(ForUserAdminMixin, self).get_queryset(request)
        if hasattr(qs, 'for_user'):
            return qs.for_user(request.user, admin=True)
        return qs

    def save_model(self, request, object, form, change):
        if change:
            if self.can_update(request, object):
                object.save()
        else:
            object.save()
