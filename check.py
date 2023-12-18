# -*- coding: utf-8 -*-

# Developed by Endika Gil
# Github:   https://github.com/endikagil/EIBmonitor
#
# The script checks for some services and network licenses status and notifies throught Telegram
# It can be added to crontab for checking every XX minutes:
# */10 * * * * /usr/bin/python3 /YourHome/EIBmonitor/check.py ##
# Use .env file to specify sensitive information: BASE_PATH, TELEGRAM_API_TOKEN, TELEGRAM_CHAT_ID

import requests     # Used for sending message using Telegram
import json         # Used to work with Telegram json response
import subprocess   # Used for checking system services status (returns status code)
import os           # Used for working with system files
import datetime     # Used for accessing to system datetime
from dotenv import load_dotenv # Used for reading .env files and hidde sensitive information
load_dotenv()

#
# Global configuration
#

BASE_PATH = os.getenv('BASE_PATH')
LOGS="/logs"
TELEGRAM_API_TOKEN=os.getenv('TELEGRAM_API_TOKEN')
TELEGRAM_CHAT_ID=os.getenv('TELEGRAM_CHAT_ID')

def sendTelegram(message, messageLOG, service):
    r = requests.post('https://api.telegram.org/bot'+TELEGRAM_API_TOKEN+'/sendMessage',
        data={'chat_id': TELEGRAM_CHAT_ID, 'text': message+service})
    data = json.loads(r.text)
    # Checking if message was sent correctly
    if data['ok']:
        if not previouslyNotified(service):
            # If was sent correctly, create flag for no more notifying about same problem
            file = open(BASE_PATH+LOGS+"/notificado"+service, "w")
            file.write("Notificado el "+str(datetime.datetime.now()))
            file.close()
    else:
        # If message could not be sent, create flag notifying it
        file = open(BASE_PATH+LOGS+"/error_al_enviar_telegram", "w")
        file.write("No se ha podido notificar "+messageLOG+service+" el "+str(datetime.datetime.now()))
        file.close()


def previouslyNotified(service):
    notifiedTelegram = os.path.isfile(BASE_PATH+LOGS+"/notificado"+service)
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
        message = "Se ha caído el demonio "
        messageLOG = "la caída del demonio "
        if not previouslyNotified(service):
            sendTelegram(message,messageLOG,service)
            os.system("sudo systemctl restart "+service)
    else:
        # Checking a warning of FOGMulticastManager service that besides service is active doest not run correctly
        if service == "FOGMulticastManager":
            there_some_error = os.system('/usr/sbin/service FOGMulticastManager status |grep "PHP Fatal error:"')
            if not there_some_error:
                if not previouslyNotified(service):
                    sendTelegram(message,messageLOG,service)
                    os.system("sudo systemctl restart "+service)

        if previouslyNotified(service):
            # If service is now active and was previously notified about was down, delete flag
            message = "Se ha levantado el demonio "
            messageLOG = "el levantamiento del demonio "
            sendTelegram(message,messageLOG,service)
            try:
                os.remove(BASE_PATH+LOGS+"/notificado"+service)
            except OSError as error:
                print(error)

def checkLicense(server):
    licenseStatus = os.popen(BASE_PATH+"/flexlm_v11.13.1.1/lmstat -a -c "+server).read().upper()
    licenseStatusFiltred = licenseStatus.find("DOWN")
    if not licenseStatusFiltred == -1:
        # license KO
        if not previouslyNotified(server):
            message = "Se ha caído la licencia "
            messageLOG = "la caída de la licencia "
            sendTelegram(message,messageLOG,server)
    else:
        if previouslyNotified(server):
            # If license is now active and was previously notified about was down, delete flag
            message = "Se ha levantado la licencia "
            messageLOG = "el levantamiento de la licencia "
            sendTelegram(message,messageLOG,server)
            os.remove(BASE_PATH+LOGS+"/notificado"+server)


# Checking services
f = open(BASE_PATH+'/servicesToCheck.txt', "r")
for line in f:
    # Ignore comments
    if not line.startswith("#"):
        checkService(line.strip())

# Checking network licenses
f = open(BASE_PATH+'/licensesToCheck.txt', "r")
for line in f:
    # Ignore comments
    if not line.startswith("#"):
        checkLicense(line.strip())
