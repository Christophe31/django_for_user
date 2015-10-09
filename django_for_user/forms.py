#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from collections import OrderedDict
from django.db.models import Q
from django.utils.translation import ugettext as _

# as we are hacking with Qs here a more explicit repr function
def q_object_to_string_list(q):
    children_list = [q.connector]
    for q_c in q.children:
        if isinstance(q_c, Q):
            children_list.append(q_object_to_string_list(q_c))
        else:
            children_list.append(q_c)
    return children_list


# here comme the hugly but handy monkey patch <3
def __repr__(self):
    return str(q_object_to_string_list(self))
Q.__repr__ = __repr__


# used to choose field to aggregate data in selects
def get_deep_attr(obj, fields):
    if not isinstance(fields, (list, tuple)):
        fields = fields.split(".")
    prev = obj
    for f in fields:
        if prev is not None:
            prev = getattr(prev, f, None)
    return prev


class ForUserBaseMixin(object):
    qs_filter_kwargs = {}
    fields_grouping = {}

    def filter_form(self, form, request, instance=None):
        query_fields = {}
        for name, field in getattr(form, 'fields', form.base_fields).items():
            if hasattr(field, "queryset"):
                query_fields[name] = field

        for name, field in query_fields.items():
            if hasattr(field.queryset, "for_user"):
                if self.qs_filter_kwargs:
                    q = field.queryset.model.for_user(
                        field.queryset, request.user, **self.qs_filter_kwargs)
                elif request.user.is_superuser:
                    q = ~Q(pk=0)
                else:
                    q = field.queryset.model.for_user(
                        field.queryset, request.user)
                if instance and getattr(instance, name + "_id", 0):
                    q |= Q(pk=getattr(instance, name + "_id"))
                elif (instance and getattr(instance, name, False) and
                        getattr(getattr(instance, name), "all", False)):
                    q |= Q(pk__in=getattr(instance, name).all().values('pk'))
                field.queryset = field.queryset.filter(q).distinct()
            if name in self.fields_grouping:
                init = [(None, field.empty_label)] if field.empty_label else []
                field.choices = init + list(self.as_group_model_choice(
                    field.queryset, *self.fields_grouping[name]))
        return form

    def as_group_model_choice(self, qs, orderings, field):
        grouped_content = OrderedDict()
        qs.order_by(*orderings)
        for e in qs:
            group_name = unicode(get_deep_attr(e, field))
            if group_name not in grouped_content:
                grouped_content[group_name] = []
            grouped_content[group_name].append((e.pk, unicode(e)))
        if ("None" in grouped_content
                and unicode(_("Other")) not in grouped_content):
            grouped_content[unicode(_("Other"))] = grouped_content["None"]
            del grouped_content["None"]
        return grouped_content.items()

    def can_update(self, request, instance):
        return (
            instance and instance.pk
            and instance._meta.model.objects.for_user(
                request.user, admin=True,
                **self.qs_filter_kwargs).filter(pk=instance.pk).exists())


class ForUserFormMixin(ForUserBaseMixin):
    def get_qs_filter_kwargs(self, request, instance=None):
        return self.qs_filter_kwargs

    def __init__(self, request, data=None, files=None, **kwargs):
        self.request = request
        if not self.qs_filter_kwargs and "filter_kwargs" in kwargs:
            self.qs_filter_kwargs = kwargs.pop("filter_kwargs")
        super(ForUserFormMixin, self).__init__(
            data=data, files=files, **kwargs)
        instance = getattr(self, "instance", None)
        self.qs_filter_kwargs = self.get_qs_filter_kwargs(request, instance)
        self.filter_form(self, request, instance)
