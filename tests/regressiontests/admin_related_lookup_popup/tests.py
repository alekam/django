"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.contrib.admin.views.main import IS_POPUP_VAR, POPUP_CALLBACK_VAR
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from models import *


class login(object):
    def __init__(self, testcase, user, password):
        self.testcase = testcase
        success = testcase.client.login(username=user, password=password)
        self.testcase.assertTrue(
            success,
            "login with username=%r, password=%r failed" % (user, password)
        )

    def __enter__(self):
        pass

    def __exit__(self, *args):
        self.testcase.client.logout()


class RelatedLookupPopupTest(TestCase):

    def setUp(self):
        User.objects.create_superuser('root', 'root@example.com', '123')
        RelatedItem.objects.create(title='lorem')
        RelatedItem.objects.create(title='ipsum')
        RelatedItem.objects.create(title='dolorem')

        AnotherRelatedItem.objects.create(title='lorem')
        AnotherRelatedItem.objects.create(title='ipsum')
        AnotherRelatedItem.objects.create(title='dolorem')
        AnotherRelatedItem.objects.create(title='lorem')
        AnotherRelatedItem.objects.create(title='ipsum')


    def test_choose_from_changelist(self):
        with login(self, 'root', '123'):
            callbacks = {
                'dismissRelatedItemLookupPopup': (reverse('admin:admin_related_lookup_popup_relateditem_changelist'), 3),
                'dismissAnoterRelatedItemLookupPopup': (reverse('admin:admin_related_lookup_popup_anotherrelateditem_changelist'), 5),
            }

            for callback_name, opts in callbacks.items():
                changelist_url, count = opts

                response = self.client.get("%s?_callback=%s" % (changelist_url, callback_name))
                self.assertContains(response, '<a href="1/">', 1, 200)
                self.assertContains(response, '<a href="2/">', 1, 200)
                self.assertContains(response, '<a href="3/">', 1, 200)
                self.assertContains(response, 'onclick="opener.%s(' % callback_name, 0, 200)

                response = self.client.get("%s?%s=1&_callback=%s" % \
                                           (changelist_url, IS_POPUP_VAR, callback_name))
                self.assertContains(response, '<a href="1/">', 0, 200)
                self.assertContains(response, '<a href="2/">', 0, 200)
                self.assertContains(response, '<a href="3/">', 0, 200)
                self.assertContains(response, 'onclick="opener.%s(' % callback_name, count, 200)


    def test_add_new_related(self):
        with login(self, 'root', '123'):
            callback_name = 'dismissRelatedItemLookupPopup'
            add_url = reverse('admin:admin_related_lookup_popup_relateditem_add')

            # check correct rendering form
            response = self.client.get("%s?_popup=1&_callback=%s" % (add_url, callback_name))
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<input type="hidden" name="_popup" value="1" />', 1, 200)
            self.assertContains(response, '<input type="hidden" name="_callback" value="%s" />' % callback_name, 1, 200)

            # check correct posting form
            response = self.client.post(add_url, {
                'title': 'zxc',
                '_popup': 1,
                '_callback': callback_name,
            })
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, '<script')
            self.assertContains(response, callback_name)


    def test_choose_new_from_changelist(self):
        with login(self, 'root', '123'):
            callback_name = 'dismissRelatedItemLookupPopup'
            changelist_url = reverse('admin:admin_related_lookup_popup_relateditem_changelist')

            response = self.client.get("%s?%s=1" % (changelist_url, IS_POPUP_VAR))
            self.assertContains(response, '"add/?_popup=1"', 1, 200)

            response = self.client.get("%s?%s=1&%s=%s" % \
                        (changelist_url, IS_POPUP_VAR, POPUP_CALLBACK_VAR, callback_name))
            self.assertContains(response, '"add/?_popup=1&_callback=%s"' % callback_name, 1, 200)

