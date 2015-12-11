__author__ = "Charlene Bertz"

import unittest
try:
    from ...main.python.main import *
except:
    from src.main.python.main import *


class UnitTest(unittest.TestCase):
    def test_pruefeBenutzerDaten(self):
        self.assertTrue(pruefeBenutzerdaten("studium","default"))

    def test_pruefeCookies(self):
        self.assertIsNone(pruefeCookies(""))

    def test_erstelleInstanz(self):
        self.assertIsNotNone(erstelleInstanz())

    def test_meldeBenutzerAn(self):
        self.assertIsNotNone(meldeBenutzerAn())