# EIBmonitor

Simple script to monitor some server services and network licenses using telegram as a notification channel.


### Requirements 📋

Make sure to create a Telegram bot.

```
https://core.telegram.org/bots/api
```
If you want to monitor some network licenses based on Flexlm technology, this package also includes a folder containing neccesary binaries.

### Installation 🔧

Install requirements

```
$ pip install -r requirements.txt
```

Change the value of Telegram Token to set yours.

```
Change <YourToken>
```

Change the value of Telegram ChatID to set yours.

```
Change <YourChatID>
```

## Configure system ⚙️

The script is designed to check every XX minutes the status of the system services and network licenses.
So, it can be added to the crontab for checking every 10 minutes, for example:
```
 */10 * * * * /usr/bin/python3 /home/YourUser/scripts/monitoringEIB/check.py
```

You can specify the network licenses hostnames you want to monitor editing _licensesToCheck.txt_.

In the same way, you can specify the name of your machine services that want to monitor and restart again editing _servicesToCheck.txt_

## Author ✒️

* **Endika Gil** - *Initial Work* - [endikagil](https://github.com/endikagil)
