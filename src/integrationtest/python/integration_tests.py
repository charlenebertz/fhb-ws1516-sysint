__author__ = 'Charlene Bertz'

from unittest import TestCase
from time import sleep
import sys
import os
try:
    from main import run_server
except:
    sys.path.append(os.path.abspath("/src/main/python"))
    import main as mainfile #path used by travis
import threading
import requests

class IntegrationTest(TestCase):
    def teste_AnmeldungUndErstelleInstanz(self):
        backGroundServer = threading.Thread(target=run_server, daemon=True)
        backGroundServer.start()
        sleep(2)
        assert backGroundServer.is_alive()
        testRequest1 = requests.get('http://127.0.0.1:8080/E2/index')
        assert testRequest1.status_code == 200
        assert testRequest1.text.find('Fehler 404') is not None


