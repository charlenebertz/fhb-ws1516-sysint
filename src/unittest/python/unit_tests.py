__author__ = "Charlene Bertz"

from unittest import TestCase
from moto import mock_s3
import boto3
import main as mainfile #path used by pybuilder



class Unittest(TestCase):
    def test_erstelleAnwendungsHTML(self):
        self.assertIsNotNone(mainfile.erstelleAnmeldungsHTML())

    @mock_s3
    def test_pruefeBenutzerdaten(self):
        s3 = boto3.resource('s3')
        s3.create_bucket(Bucket='fhb-bu')
        s3.Object('fhb-bu', 'passwd').put(Body='student:passwd')
        assert mainfile.pruefeBenutzerdaten('student','passwd') == True
        assert mainfile.pruefeBenutzerdaten('keinStudent','dwssap') == False