from unittest import TestCase
from django.test import Client


class Views_Test(TestCase):

    def test_dataset_view(self):
        client = Client()
        response = client.get('/dataset')
        self.assertEqual(response.status_code, 200, msg="error in dataset page")

    def test_mapping_view(self):
        client = Client()
        response = client.get('/mapping')
        self.assertEqual(response.status_code, 200, msg="error in mapping page")

    def test_execute_view(self):
        client = Client()
        response = client.get('/execute')
        self.assertEqual(response.status_code, 200, msg="error in execute page")


