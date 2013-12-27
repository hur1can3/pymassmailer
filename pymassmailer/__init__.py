# -*- coding: utf-8 -*-
from jinja2 import Environment, PackageLoader, TemplateNotFound
from marrow.mailer import Mailer, Message
from smtplib import SMTPException, SMTPAuthenticationError
from date import datetime
import os
import logging
import base64
import sspi
import string


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


class MessageAttribute(object):
    # A list of MIME-encoded attachments.
    #attachments = []
    # The visible author of the message. This maps to the From: header.
    author = ''
    # The visible list of primary intended recipients.
    to = []
    # A visible list of secondary intended recipients.
    cc = []
     # An invisible list of tertiary intended recipients.
    bcc = []
    # The visible date/time of the message, defaults to datetime.now()
    date = datetime.now()
    # A list of MIME-encoded embedded images.
    #embedded = []
    # Unicode encoding, defaults to utf-8.
    encoding = 'utf-8'
     # A list of additional message headers.
    headers = []
    # The address that message disposition notification messages get routed to.
    notify = ''
    # An extended header for an organization name.
    organization = ''
    # The X-Priority header.
    priority = []
    # The address replies should be routed to by default;
    reply = []
    # The number of times the message should be retried in the event of a
    # non-critical failure.
    retries = 0
    # The designated sender of the message; may differ from author. This is
    # primarily utilized by SMTP delivery.
    sender = ''
    # The subject of the message.
    subject = ''


class PyMassMailer(object):

    """
    Main wrapper around marrow.mailer and jinja2.

    This should be run once in the global scope as it inits marrow and Jinja
    """

    def __init__(self, pkg_name, config=None,  server='localhost',
                 username=None, password=None, email_port=25,
                 default_sender=None, template_dir='email_templates'):
        """
        Can be created by passing the configuration for sending a mail,
        pkg_name is required so we can find your email templates but depending
        on your configuration server, username, password may not be required.

        Only server, username, password, port, sender and template_dir can be
        configured.  If you need to change other settings such as logging.
        Please pass a Config object.
        """
        if not config is None:
            self._config = config
        else:
            self._config = Config()
            if not server is None:
                self._config.EMAIL_HOST = server
            if not username is None:
                self._config.EMAIL_USERNAME = username
            if not password is None:
                self._config.EMAIL_PWD = password
            if not email_port is None:
                self._config.EMAIL_PORT = email_port
            if not default_sender is None:
                self._config.EMAIL_SENDER = default_sender
            self._config.EMAIL_TEMPLATE_DIR = template_dir

        # Init log
        self._log = logging.getLogger(self._config.LOGGER_NAME)
        self._log.setLevel(self._config.LOGGER_LEVEL)
        console_handler = logging.StreamHandler()
        self._log.addHandler(console_handler)

        # Init Jinja
        self._jinja_env = Environment(loader=PackageLoader(pkg_name,
                                                           self._config.EMAIL_TEMPLATE_DIR))

        # Init Mailer
        self._mailer = Mailer(dict(
            transport=dict(
                use='smtp',
                host=self._config.EMAIL_HOST,
                username=self._config.EMAIL_USERNAME,
                password=self._config.EMAIL_PWD,
                port=self._config.EMAIL_PORT),
            manager=dict()))

        self._mailer.start()

    def asbase64(msg):
        return string.replace(base64.encodestring(msg), '\n', '')

    def connect_to_exchange_as_current_user(self, smtp):
        # Send the SMTP EHLO command
        code, response = smtp.ehlo()
        if code != self._config.SMTP_EHLO_OKAY:
            raise SMTPException(
                "Server did not respond as expected to EHLO command")

        sspiclient = sspi.ClientAuth('NTLM')

        # Generate the NTLM Type 1 message
        sec_buffer = None
        err, sec_buffer = sspiclient.authorize(sec_buffer)
        ntlm_message = self.asbase64(sec_buffer[0].Buffer)

        # Send the NTLM Type 1 message -- Authentication Request
        code, response = smtp.docmd("AUTH", "NTLM " + ntlm_message)

        # Verify the NTLM Type 2 response -- Challenge Message
        if code != self._config.SMTP_AUTH_CHALLENGE:
            raise SMTPException(
                "Server did not respond as expected to NTLM negotiate message")

        # Generate the NTLM Type 3 message
        err, sec_buffer = sspiclient.authorize(base64.decodestring(response))
        ntlm_message = self.asbase64(sec_buffer[0].Buffer)

        # Send the NTLM Type 3 message -- Response Message
        #code, response = smtp.docmd("", ntlm_message)
        code, response = smtp.docmd(ntlm_message)
        if code != self._config.SMTP_AUTH_OKAY:
            raise SMTPAuthenticationError(code, response)

    def send_email(self, send_to, template, subject, files=[], **kwargs):
        """
            Sends an email to the target email with two types
                1) HTML
                2) Plain

            We will try the template with .html for rich and .txt for plain,
            if one isn't found we will only send the
            correct one.

            Both will rendered with Jinja2
        """

        message = Message(author=self._config.EMAIL_SENDER, to=send_to)
        message.subject = subject

        if len(files) > 0:
            for f in files:
                #part = MIMEBase('application', "octet-stream")
                #part.set_payload( open(f,"rb").read() )
                # Encoders.encode_base64(part)
                filename = os.path.basename(f)
                #part.add_header('Content-Disposition', 'attachment; filename="%s"' % filename)
                message.attach(filename, data=f)

        try:
            rendered_template = self._jinja_env.get_template(template + '.txt')
            message.plain = rendered_template.render(**kwargs)
            self._log.debug('Plain text email is %s', message.plain)
        except TemplateNotFound:
            self._log.debug('txt template not found')

        try:
            rendered_template = self._jinja_env.get_template(
                template + '.html')
            message.rich = rendered_template.render(**kwargs)
            self._log.debug('html email generated %s' % message.rich)
        except TemplateNotFound:
            self._log.debug('html template not found')

        self._mailer.send(message)
