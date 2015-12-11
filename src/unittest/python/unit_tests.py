__author__ = "Charlene Bertz"

import unittest
import main.python.main as mainfile


class UnitTest(unittest.TestCase):
    def test_pruefeBenutzerDaten(self):
        self.assertTrue(mainfile.pruefeBenutzerdaten("studium","default"))

    def test_pruefeCookies(self):
        self.assertIsNone(mainfile.pruefeCookies(""))

    def test_erstelleInstanz(self):
        self.assertIsNotNone(mainfile.erstelleInstanz())

    def test_meldeBenutzerAn(self):
        self.assertIsNotNone(mainfile.meldeBenutzerAn())