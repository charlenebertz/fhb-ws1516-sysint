import configparser
import os

class AWSAnmeldung():
    def __init__(self,benutzer,account):
        self.benutzer = benutzer
        self.account = account
        configName = "credentials"
        configPfad = os.path.join("/","home",self.benutzer,".aws",configName)

        self.config = configparser.ConfigParser()
        self.config.read(configPfad)
        self.aws_access_key_id = self.leseEintrag(account,"aws_access_key_id")
        self.aws_secret_access_key = self.leseEintrag(account,"aws_secret_access_key")
        self.region_name = self.leseEintrag(account,"region_name")

    def leseEintrag(self,auswahl,zeile):
        self.config.get(auswahl,zeile)
        return self.config.get(auswahl,zeile)

if __name__ == '__main__':
    test = AWSAnmeldung("studium","default")
    print(test.aws_secret_access_key,test.aws_access_key_id)
    print(test.leseEintrag("default","aws_access_key_id"))