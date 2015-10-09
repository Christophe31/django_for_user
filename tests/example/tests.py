#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.test import TestCase, RequestFactory, Client as HttpClient
from django.contrib.auth.models import User, Permission

from .models import Client, Region, Group
from . import forms


class ExportTest(TestCase):
    def setUp(self):
        # init tools
        self.requests = RequestFactory()
        self.client = HttpClient()

        # init DB
        self.admin = User.objects.create_user(
            "admin", "admin@admin.com", "passwd")
        self.user_1 = User.objects.create_user(
            "user_1", "admin@admin.com", "passwd")
        self.user_1.user_permissions.add(*Permission.objects.all())
        self.user_1.is_staff = True
        self.user_1.is_superuser = False
        self.user_1.save()
        self.user_2 = User.objects.create_user(
            "user_2", "admin@admin.com", "passwd")
        self.admin.is_superuser = True
        self.admin.is_staff = True
        self.admin.save()
        self.client_1 = Client(name="client_1")
        self.client_1.save()
        self.region_1 = Region(name="region_1", client=self.client_1)
        self.region_1.save()
        self.group_1 = Group(name="group_1",region=self.region_1)
        self.group_1.save()
        self.group_1.users.add(self.user_1)
        self.group_1.save()

        self.client_2 = Client(name="client_2")
        self.client_2.save()
        self.region_2 = Region(name="region_2", client=self.client_2)
        self.region_2.save()
        self.group_2 = Group(name="group_2",region=self.region_2)
        self.group_2.save()
        self.group_2.users.add(self.user_2)
        self.group_2.save()

    def test_for_user_qs(self):
        self.assertEqual(Group.objects.for_user(self.user_1).count(), 1)
        self.assertEqual(Group.objects.for_user(self.user_2).count(), 1)
        self.assertEqual(Group.objects.for_user(self.admin).count(), 2)
        repr(Client.for_user(self.user_1))

    def test_for_user_form(self):
        request = self.requests.get("/")
        request.user = self.admin
        str(forms.GroupForm(request))
        request.user = self.user_1
        str(forms.GroupForm(request, instance=self.group_1))
        forms.GroupForm.qs_filter_kwargs = {"site_id": 18}
        form = forms.GroupForm(request, data={
            "name": "group_1'",
            "region": self.region_2.pk,
            "users": [self.user_1.pk]})
        self.assertFalse(form.is_valid())
        form = forms.GroupForm(request, data={
            "name": "group_1'",
            "region": self.region_1.pk,
            "users": [self.user_1.pk]})
        self.assertTrue(form.is_valid())

    def test_for_user_admin(self):
        self.client.login(username='user_1', password='passwd')
        resp = self.client.get("/admin/example/group/{}/".format(self.group_1.pk))
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get("/admin/example/group/".format(self.group_1.pk))
        self.assertEqual(resp.status_code, 200)
