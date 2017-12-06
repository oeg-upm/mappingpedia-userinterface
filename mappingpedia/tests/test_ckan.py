import os
from unittest import TestCase
import requests
from mappingpedia.views import get_organizations


class CKAN_Tests(TestCase):

    def test_list_organizations(self):
        organizations = get_organizations()
        self.assertNotEqual(organizations, [], msg='CKAN return an empty list of organization or is down')




