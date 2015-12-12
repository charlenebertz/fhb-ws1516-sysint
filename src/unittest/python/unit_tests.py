__author__ = "Charlene Bertz"

from unittest import TestCase
from main import erstelleAnmeldungsHTML

class Unittest(TestCase):
    def test_erstelleAnwendungsHTML(self):
        self.assertIsNotNone(erstelleAnmeldungsHTML())