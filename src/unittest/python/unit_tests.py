__author__ = "Charlene Bertz"

from unittest import TestCase
import src.main.python.main as mainfile

class Unittest(TestCase):
    def test_erstelleAnwendungsHTML(self):
        self.assertIsNotNone(mainfile.erstelleAnmeldungsHTML())