__author__ = 'Charlene Bertz'

from unittest import TestCase
import boto3
from moto import mock_s3
from main import pruefeCookies
import json

class ComponenTest(TestCase):

    @mock_s3
    def test_pruefeCookies(self):
        s3 = boto3.resource('s3')
        s3.create_bucket(Bucket='fhb-bu')
        s3.Object('fhb-bu', 'passwd').put(Body='student:passwd')
        assert pruefeCookies(json.dumps({'benutzer':'student','password':'passwd'})) == True
        assert pruefeCookies(json.dumps({'benutzer':'lehrer','password':'Riesenknall2012'})) == False