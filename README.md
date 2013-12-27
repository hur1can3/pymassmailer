pymassmailer
=================

Matthew Levandowski - December 2013

Overview
--------

pymassmailer is a generic mass mailer app which can use html jinja2 templates for data.

It sends an email to the target email with two types
                1) HTML
                2) Plain

We will try the template with .html for rich html and .txt for plain,
if one isn't found we will only send the correct one.

Both will rendered with Jinja2

Py Mass Mailer Can be created by passing the configuration for sending a mail, pkg_name is required so we can find your email templates but depending on your configuration server, username, password may not be required.

Only server, username, password, port, sender and template_dir can be configured.  If you need to change other settings such as logging. Please pass a Config object.

Config object is specified below:
class Config(object):

    """
        Py Mass Mailer configuration
    """
    EMAIL_HOST = 'localhost'
    EMAIL_USERNAME = ''
    EMAIL_PWD = ''
    EMAIL_PORT = 25
    EMAIL_SENDER = ''
    EMAIL_TEMPLATE_DIR = ''
    LOGGER_NAME = 'pymassmailer'
    LOGGER_LEVEL = logging.NOTSET
    DEBUG_LEVEL = 0
    SMTP_EHLO_OKAY = 250
    SMTP_AUTH_CHALLENGE = 334
    SMTP_AUTH_OKAY = 235

 To set just use config = pymassmailer.config(EMAIL_HOST='someserver', ...)

Installation instructions
-------------------------

Add the following to the INSTALLED_APPS in the settings.py of your project:

>>> pip install pymassmailer


Example Usage instructions
---------------------------------------

I have a sample below that loads an excel file with pandas and mass mails the emails from it:

Example script:

```python
import PyMassMailer
import os
import pandas as pd

SMTP_SERVER = 'localhost'
TEMPLATE_DIR = os.path.dirname(os.path.abspath(__file__)) + '\\templates'
TEMPLATE_NAME = 'message'
FROM_ADDR = "individualbusiness@somewhere.com"
SUBJECT = "Reminder: Waiting for Information."
SOURCE_FILE = 'mailmerge-final.xls'

data = pd.read_excel(SOURCE_FILE, 'Master')

# Setup mass mailer class
email_sender = PyMassMailer(__name__, server=SMTP_SERVER, default_sender=FROM_ADDR, template_dir=TEMPLATE_DIR)

# loop through email addresses
for count,row in data.iterrows():
	print row
	TO_ADDR = row['Email']
	print 'sending email to: %s' % TO_ADDR
 	email_sender.send_email(TO_ADDR, TEMPLATE_NAME, SUBJECT , name=row['Name'])
```

and in templates dir

layout.html
```html
<html>
<head>
    <!-- <meta http-equiv="Content-Type" content="text/html; charset=utf-8" /> -->
    <meta http-equiv="content-type" content="text/html; charset=ISO-8859-1">
    <meta name="viewport" content="width=device-width">
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```


message.html
```html
{% extends "layout.html" %}

{% block content %}

    <p>Hello, {{ name }}!</p>
    <br>

{% endblock %}

```

message.txt
'''
 Hello, {{ name}}
'''