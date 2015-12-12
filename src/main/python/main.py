__author__ = 'Benjamin Urbanek'

import boto3
from bottle import get, post, request, route,run, response
import config
import subprocess

import json
aws = config.AWSAnmeldung("studium","default")


session = boto3.Session(aws_access_key_id=aws.aws_access_key_id,aws_secret_access_key=aws.aws_secret_access_key,region_name=aws.region_name)
ec2 = session.resource('ec2')
ec2Client = session.client('ec2')
s3 = session.resource('s3')
s3Client = session.client('s3')

instanzListe = ["t2.micro","t2.small","t2.medium","t2.large","c4.large","r3.large","i2.xlarge","g2.2xlarge"]


secret = "a673043e4b932aa51b4c5019b748dc20"

fehlercode = "Fehler 404"

def pruefeCookies(cookie):
    if cookie:
        tmpListe = json.loads(cookie)
        if pruefeBenutzerdaten(tmpListe["benutzer"],tmpListe["password"]):
            return True
    return False



@route('/E2/index')
def generiereAnsicht():
    idInstanz = request.query.id or None
    befehlInstanz = request.query.befehl or None
    parameterInstanz = request.query.parameter or None

    pruefeCookies(request.get_cookie("account",secret=secret))

    if  not pruefeCookies(request.get_cookie("account",secret=secret)):
        return erstelleHTML(fehlercode)

    if befehlInstanz and idInstanz:
        if befehlInstanz =="starten":
            starteInstanz(idInstanz)
        elif befehlInstanz == "stoppen":
            stopInstanz(idInstanz)
        elif befehlInstanz == "terminieren":
            terminateInstanz(idInstanz)
        elif befehlInstanz == "erstelleImage":
            if parameterInstanz:
                createImage(idInstanz,parameterInstanz)

    html = """

    <script>
        function getImageName(id) {
            var image = prompt("Please enter image name", "");
            if (image != null) {
                window.location.href ='/E2/index?befehl=erstelleImage&parameter='+image+'&id='+id;
            }
        }
    </script>


    <h1>Instances</h1>

    <br>
    <img class="list_icon" src="https://s3-us-west-2.amazonaws.com/fhb-bu/img/plus.png" title="start instance"/> Start Instance
    <br><br>

    <table id="instances" class="list background_gradient" style="width: 100%;">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Type</th>
            <th>Status</th>
            <th>IP</th>
            <th>DNS</th>
            <th>Image</th>
            <th>Security Groups</th>
            <th style="width: 100px;">Options</th>
        </tr>
    """
    for instance in ec2.instances.all():
        public_ip_address= instance.public_ip_address
        if not public_ip_address:
            public_ip_address = ""
        public_dns_name = instance.public_dns_name
        if not public_dns_name:
            public_dns_name = ""
        tag = ""
        if instance.tags:
            tag = instance.tags[0]['Value']

#        print(instance.tags)

        html += """
        <tr class="list_instance">
            <td>"""+instance.id+"""</td>
            <td>"""+tag+"""</td>
            <td>"""+instance.instance_type+"""</td>
            <td>"""+instance.state['Name']+"""</td>
            <td>"""+public_ip_address+"""</td>
            <td>"""+public_dns_name+"""</td>
            <td>"""+instance.image_id+"""</td>

            <td>
                <ul>
        """


        #loop to list all used security groups


        if len(instance.security_groups) > 1:
            for zeile in instance.security_groups:
                html += """
                        <li>{0}</li>
                    """.format(zeile["GroupName"])
        elif len(instance.security_groups) == 1:
            zeile = instance.security_groups[0]
            html += """
                        <li>{0}</li>
                    """.format(zeile["GroupName"])
        else:
            html += """
                        <li> </li>
                    """

        #save_image-icon does not do anything right now
        html += """
                    </ul>
                </td>
                <td>
                    <img class="list_icon" src="https://s3-us-west-2.amazonaws.com/fhb-bu/img/save_image.png" title="save image" onclick="getImageName('{0}')"/>
                    <div class="list_icon_blank"></div>
        """.format(instance.id)

        #show only start/stop depending on status



        if instance.state['Name'] == "stopped":
            html += """
                    <a href='/E2/index?id="""+instance.id+"""&befehl=starten'>
                        <img class='list_icon' src='https://s3-us-west-2.amazonaws.com/fhb-bu/img/start.png' title='start'/>
                    </a>
        """
        elif instance.state['Name'] == "running":
            html += """
                    <a href='/E2/index?id="""+instance.id+"""&befehl=stoppen'>
                        <img class='list_icon' src='https://s3-us-west-2.amazonaws.com/fhb-bu/img/stop.png' title='stop'/>
                    </a> """

        html += """
                    <div class="list_icon_blank"></div>
                    <a href='/E2/index?id="""+instance.id+"""&befehl=terminieren'>
                        <img class='list_icon' src='https://s3-us-west-2.amazonaws.com/fhb-bu/img/terminate.png' title='terminate'/>
                    </a>
                </td>
            </tr>
        """
    html += """</table>"""


    return erstelleHTML(html)

@route('/E2/Anmeldung' ,method="POST")
def zeigeBenutzerAnmeldung():
    benutzer = request.forms.benutzer or None
    password = request.forms.password or None
    if benutzer and password:
        html = erstelleAnmeldungsHTML()
        if pruefeBenutzerdaten(benutzer,password):
            html="Angemeldet"
            response.set_cookie("account", json.dumps({'benutzer': benutzer, 'password': password}), secret=secret)
    return erstelleHTML(html)


@route('/E2/Anmeldung',method="GET")
def meldeBenutzerAn():
    html = erstelleAnmeldungsHTML()
    return erstelleHTML(html)

@route('/E2/erstelleInstanz')
def erstelleInstanz():
    id = request.query.id or None
    userData = request.query.userData or None
    securityGroups = request.query.securityGroups or None
    keyName = request.query.keyName or None
    instanceType = request.query.instanceType or None

    if not pruefeCookies(request.get_cookie("account",secret=secret)):
        return erstelleHTML(fehlercode)

    if id and userData and securityGroups:
        if instanceType:
            createInstanz(id,userData,securityGroups,keyName,instanceType=instanceType)
        else:
            createInstanz(id,userData,securityGroups,keyName)

    html = """

    <h1>Start Instance</h1>
    <form>
        <table>
            <tr>
                <td>Name</td>
                <td><input type='text' name='userData'></td>
            </tr>
     """
    html += """<tr>
                <td>Operating Systems</td>
                <td>
                    <select name="id">
                    <option value=ami-f0091d91>Amazon Linux</option>
                    <option value=ami-4dbf9e7d>Redhat Linux</option>
                    <option value=ami-d7450be7>Suse Linux</option>
                    <option value=ami-5189a661>Ubuntu Linux</option>
                    <option value=ami-f0091d91>Microsoft Server 2012</option>
                    </select>
                </td>
            </tr>
            <tr>
                <td>Instance Type</td>
                <td>
                    <select name="instanceType">
    """
    #loop to list instance types that can be started
    for zeile in instanzListe:
       html += """
                        <option value="""+zeile+""">"""+zeile+"""</option>
    """

    html += """
                    </select>
                </td>
            </tr>
            <tr>
                <td>Security Group</td>
                <td>
                    <select name="securityGroups">

    """

    #loop to list security groups that can be selected
    tmpListe = []
    for zeile in ec2.security_groups.all():
        if not zeile.group_name in tmpListe:
            tmpListe.append(zeile.group_name)
            html += """
                        <option value="""+zeile.group_name+""">"""+zeile.group_name+"""</option>
    """


    html += """
                    </select>
                </td>
            </tr>
            <tr>
                <td>Key Pair</td>
                <td>
                    <select name="keyName">

    """

    #loop to list keys that can be selected
    for zeile in holeSchluesselNamen():
        html += """
                        <option value="""+zeile+""">"""+zeile+"""</option>
    """

    html += """
                    </select>
                </td>
            </tr>
            <tr>
                <td colspan="2"><input type='submit' value='Start'></td>
            </tr>
        </table>
    </form>
    """
    return erstelleHTML(html)


def erstelleAnmeldungsHTML():
    html = """
    <h1>Sign In</h1>
    <form action='./Anmeldung' method='post'>
        <table>
            <tr>
                <td>User</td>
                <td><input type='text' name='benutzer'></td>
            </tr>
            <tr>
                <td>Password</td>
                <td><input type='text' name='password'></td>
            </tr>
            <tr>
                <td colspan="2"><input type='submit' value='Sign In'></td>
            </tr>
        </table>
    </form>
    """
    return html

def pruefeBenutzerdaten(benutzer,password):
    bucket = s3.Bucket("fhb-bu")
    bucket.download_file("passwd","passwd")
    datei = open("passwd","r")
    for zeile in datei.readlines():
        zeile = zeile.replace("\n","")
        zeile.replace("\r","")
        s3Benutzer,s3Password = zeile.split(":")
        if password == s3Password and benutzer == s3Benutzer:
            return True
    return False

def erstelleHTML(inhalt):
    header = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
        <head>
            <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
            <title>Systemintegration</title>

            <link rel="stylesheet" href="https://s3-us-west-2.amazonaws.com/fhb-bu/layout.css">
        </head>
        <body>
            <table id="wrapper">
                    <tr>
                        <td id="layout_shadow_left" class="background_crossedLines" rowspan="2"></td>
                        <td id="layout_container">
                            <div id="layout_header">
                                <div id="layout_topBar">
                                    <div id="layout_topMenu"> <!-- MENU AREA -->
                                        <div class='dropDownMenu'>
                                            <ul>
                                                <li class='dropDownMenuSubLink'>
                                                    <a href='/E2/Anmeldung'>Sign In</a>
                                                </li>
                                                <li class='dropDownMenuSubLink'>
                                                    <a href='/E2/index'>Instances</a>
                                                    <ul>
                                                        <li class='dropDownMenuSubLink'>
                                                            <a href='/E2/index'>Overview</a>
                                                        </li>
                                                        <li class='dropDownMenuSubLink'>
                                                            <a href='/E2/erstelleInstanz'>Start Instance</a>
                                                        </li>
                                                    </ul>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div id="layout_content"> <!-- CONTENT AREA -->
                            """
    footer = """
                        </div>
                    </td>
                    <td id="layout_shadow_right" class="background_crossedLines" rowspan="2"></td>
                </tr>
                <tr>
                    <td id="layout_footer"> <!-- FOOTER AREA -->
                        Project by<br>
                        <pre>Charlene Bertz    Florian Bieder    Frauke Albert    Benjamin Urbanek</pre>
                    </td>
                </tr>
            </table>
        </body>
    </html>
    """
    return header+"\n"+inhalt+"\n"+footer

def starteInstanz(id):
    ec2Client.start_instances(InstanceIds=[id])

def stopInstanz(id):
    ec2Client.stop_instances(InstanceIds=[id])

def terminateInstanz(id):
    ec2Client.terminate_instances(InstanceIds=[id])

def createImage(id,name):
    ec2Client.create_image(InstanceId=id,Name=name)

def createInstanz(id,userdata,securityGroups,keyName,countMin=1,countmax=1,instanceType='t2.micro'):
    instanz = ec2.create_instances(ImageId=id,SecurityGroupIds=[securityGroups],MinCount=countMin,MaxCount=countmax,InstanceType=instanceType,KeyName=keyName)
    if instanz:
        instanz[0].create_tags(Tags=[{'Key':'Name','Value':userdata}])

def holeSchluesselNamen():
    returnliste = []
    for zeile in ec2Client.describe_key_pairs()['KeyPairs']:
        returnliste.append(zeile['KeyName'])
    return returnliste


#instance = ec2.create_instances(ImageId="ami-2cecff4d",MinCount=1,MaxCount=1,InstanceType='t2.micro',SecurityGroupIds=['standart'],KeyName="fhb-aws")
port = 8080
hostname = "127.0.0.1"
run(host=hostname, port=port)


