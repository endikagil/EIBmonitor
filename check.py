# -*- coding: utf-8 -*-

# Developed by Endika Gil
# Github:   https://github.com/endikagil/monitoringEIB
#
# The script checks for some services and network licenses status and notifies throught Telegram
# It can be added to crontab for checking every XX minutes:
# */10 * * * * /usr/bin/python3 /home/YourUser/scripts/monitoringEIB/check.py ##

import requests     # Used for sending message using Telegram
import json         # Used to work with Telegram json response
import subprocess   # Used for checking system services status (returns status code)
import os           # Used for working with system files
import datetime     # Used for accessing to system datetime

#
# Global configuration
#

BASE="/home/YourUser/scripts/monitoringEIB/"
LOGS="logs"

def sendTelegram(element, service):
    if element == "service":
        r = requests.post('https://api.telegram.org/bot<YourToken>/sendMessage',
            data={'chat_id': '<YourChatID>', 'text': 'El demonio '+service+' está caído'})
        data = json.loads(r.text)
        # Checking if message was sent correctly
        if data['ok']:
            # If was sent correctly, create flag for no more notifying about same problem
            file = open(BASE+LOGS+"/notificado"+service, "w")
            file.write("Notificado el "+str(datetime.datetime.now()))
            file.close()
        else:
            # If message could not be sent, create flag notifying it
            file = open(BASE+LOGS+"/error_al_enviar_telegram", "w")
            file.write("No se ha podido notificar la caída del demonio "+service+" el "+str(datetime.datetime.now()))
            file.close()
    if element == "license":
        r = requests.post('https://api.telegram.org/bot<YourToken>/sendMessage',
            data={'chat_id': '<YourChatID>', 'text': 'La license '+service+' está caída'})
        data = json.loads(r.text)
        # Checking if message was sent correctly
        if data['ok']:
            # If was sent correctly, create flag for no more notifying about same problem
            file = open(BASE+LOGS+"/notificado"+service, "w")
            file.write("Notificado el "+str(datetime.datetime.now()))
            file.close()
        else:
            # If message could not be sent, create flag notifying it
            file = open(BASE+LOGS+"/error_al_enviar_telegram", "w")
            file.write("No se ha podido notificar la caída de la license "+service+" el "+str(datetime.datetime.now()))
            file.close()

def previouslyNotified(service):
    notifiedTelegram = os.path.isfile(BASE+LOGS+"/notificado"+service)
    if notifiedTelegram:
        return True
    else:
        return False

def checkService(service):
    p = subprocess.Popen(["systemctl", "is-active",  service],
                        stdout=subprocess.PIPE)
    (output, err) = p.communicate()
    output = output.decode('utf-8')
    if output.strip() != "active":
        if not previouslyNotified(service):
            sendTelegram("service",service)
            os.system("sudo systemctl restart "+service)
    else:
        # Checking a warning of FOGMulticastManager service that besides service is active doest not run correctly
        if service == "FOGMulticastManager":
            there_some_error = os.system('service FOGMulticastManager status |grep "PHP Fatal error:"')
            if not there_some_error:
                if not previouslyNotified(service):
                    sendTelegram("service",service)
                    os.system("sudo systemctl restart "+service)

        if previouslyNotified(service):
            # If service is now active and was previously notified about was down, delete flag
            os.remove(BASE+LOGS+"/notificado"+service)

def checkLicense(server):
    licenseStatus = os.popen(BASE+"/flexlm_v11.13.1.1/lmstat -a -c "+server).read().upper()
    licenseStatusFiltred = licenseStatus.find("DOWN")
    if not licenseStatusFiltred == -1:
        # license KO
        if not previouslyNotified(server):
            sendTelegram("license",server)
    else:
        if previouslyNotified(server):
            # If license is now active and was previously notified about was down, delete flag
            os.remove(BASE+LOGS+"/notificado"+server)


# Checking services
f = open('servicesToCheck.txt', "r")
for line in f:
    # Ignore comments
    if not line.startswith("#"):
        checkService(line.strip())

# Checking network licenses
f = open('licensesToCheck.txt', "r")
for line in f:
    # Ignore comments
    if not line.startswith("#"):
        checkLicense(line.strip())
