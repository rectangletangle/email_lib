''' This module contains the main email handling classes. This module basically
    does all the heavy lifting. '''


import os
import socket
import smtplib
import email
import mimetypes

import email_lib.constants as constants
import email_lib.iso_time as iso_time

__all__ = ['Attachment', 'Message', 'EmailServer']

class Attachment (object) :
    ''' This is the email attachment class, arbitrary files can be attached to
        an email message (<Message>) using this class. This is simply a facade
        for the <email.MIMEBase.MIMEBase> class.

        <path>         : A path to the attachment file.
        <read_mode>    : Read the file as plain text, or as a binary
                         (<'plain'>, <'binary'>).
        <type_>        : A MIME content-type string. (A type is guessed if
                         nothing is given)
        <default_type> : The MIME content-type used if none are given, and none
                         can be guessed. '''

    _is_attachment = True

    def __init__ (self, path, read_mode='plain', type_=None,
                  default_type=constants.MIME_TYPE_TEXT) :
        self.path         = path
        self.read_mode    = read_mode
        self.type         = type_
        self.default_type = default_type

    def __str__ (self) :
        return self.make().as_string()

    def __unicode__ (self) :
        return unicode(self.make().as_string())

    def _read (self, attachment, path) :
        with open(path, 'r') as attachment_file :
            file_content = attachment_file.read()
            attachment.set_payload(file_content)
            return file_content

    def _read_binary (self, attachment, path) :
        with open(path, 'rb') as attachment_file :
            file_content = attachment_file.read()
            attachment.set_payload(file_content)
            email.Encoders.encode_base64(attachment)
            return file_content

    _read_modes = {'plain' : _read,
                   'p'     : _read,
                   'r'     : _read,

                   'binary' : _read_binary,
                   'bin'    : _read_binary,
                   'b'      : _read_binary,
                   'rb'     : _read_binary}

    def _handle_mime_content_type (self, path, content_type, default_type) :
        if content_type is None :
            guessed_type = mimetypes.guess_type(path)[0]

            if guessed_type is not None :
                if guessed_type != 'image/x-png' :
                    content_type = guessed_type
                else :
                    # Standard non-experimental types are preferable.
                    content_type = constants.MIME_TYPE_PNG_IMAGE
            else :
                content_type = default_type

        try :
            type_, subtype = str(content_type).lower().split('/')
        except ValueError :
            raise ValueError('The MIME content-type was not valid.')
        else :
            return type_, subtype

    def _make (self, path, read_mode, content_type, default_type, basename) :
        type_, subtype = self._handle_mime_content_type(path, content_type,
                                                        default_type)

        attachment = email.MIMEBase.MIMEBase(type_, subtype)

        try :
            read_func = self._read_modes[str(read_mode).lower()]
        except KeyError :
            raise KeyError("The read mode must be <'plain'> or <'binary'>.")
        else :
            read_func(self, attachment, path)

            attachment.add_header('Content-Disposition',
                                  'attachment; filename=%s' % basename)

            # This is only needed once in a multipart message.
            del attachment['MIME-Version']

            return attachment

    def basename (self) :
        ''' This returns <self.path>'s US-ASCII encoded basename (as outlined
            in RFC 2183 pg 3) '''

        return os.path.basename(self.path).encode(constants.ASCII)

    def make (self) :
        ''' This makes and returns a MIME attachment object based off of the
            <email.MIMEBase.MIMEBase> class. '''

        attachment = self._make(self.path, self.read_mode, self.type,
                                self.default_type, self.basename())
        return attachment

class _BaseContainer (object) :
    ''' An abstract base class for list based container classes. Inheriting
        classes should have a <_get_container> method, which should return the
        container list. '''

    def __contains__ (self, item) :
        return item in self._get_container()

    def __iter__ (self) :
        return iter(self._get_container())

    def __len__ (self) :
        return len(self._get_container())

    def __getitem__ (self, index) :
        return self._get_container()[index]

class _Recipients (_BaseContainer) :
    ''' This class manages a unique list of recipient email addresses. '''

    def __init__ (self, recipients) :
        self._recipients = self._make(recipients)

        self.delimiter = u', '

    def __str__ (self) :
        return str(self.delimiter).join(self._recipients)

    def __unicode__ (self) :
        return unicode(self.delimiter).join(self._recipients)

    def _get_container (self) :
        return self._recipients

    def _remove_duplicates (self, recipients) :
        unique_recipients = []
        for recipient in recipients :
            unicode_recipient = unicode(recipient)
            if unicode_recipient not in unique_recipients :
                unique_recipients.append(unicode_recipient)

        return unique_recipients

    def _make (self, recipients) :
        if isinstance(recipients, basestring) :
            # <recipients> is treated as a single recipient.
            recipient  = recipients
            recipients = [recipient]

        unique_recipients = self._remove_duplicates(recipients)

        return unique_recipients

class Message (object) :
    ''' This class creates a message object with the proper MIME headers. This
        is just a facade for the <email.MIMEMultipart.MIMEMultipart> class.

        <from_>       : The "from" address, this should be a single string.
        <to>          : The address(es) of the recipient(s). A string is
                        treated as a single recipient, while a list of strings
                        is treated as multiple recipients. Duplicate recipients
                        will be omited.
        <subject>     : The message's subject text.
        <body>        : The text that comprises the message's body.
        <attachments> : The message's attachments. This can either be a single
                        <Attachment> object, or a list of <Attachment>
                        objects. '''

    _is_message = True

    def __init__ (self, from_, to, subject=u'', body=u'', attachments=()) :
        self.from_       = from_
        self.to          = to
        self.subject     = subject
        self.body        = body
        self.attachments = attachments

    def __str__ (self) :
        ''' This returns the message as a MIME formatted string.

            Note : There is no <Return-Path> header, because it's normally
                   handled by the server. '''

        return self.make().as_string()

    def __unicode__ (self) :
        ''' This returns the message as a MIME formatted unicode string.

            Note : There is no <Return-Path> header, because it's normally
                   handled by the server. '''

        return unicode(self.make().as_string())

    def __add__ (self, other) :
        return unicode(self.make().as_string()) + unicode(other)

    def __radd__ (self, other) :
        return unicode(other) + unicode(self.make().as_string())

    def _encoding (self, text) :
        for encoding in constants.ENCODINGS :
            try :
                text.encode(encoding)
            except UnicodeError :
                continue
            else :
                break

        return encoding

    def _as_mime_text (self, text) :
        encoding  = self._encoding(text)
        mime_text = email.MIMEText.MIMEText(text.encode(encoding),
                                            _subtype='plain',
                                            _charset=encoding)

        # This is only needed once in a multipart message.
        del mime_text['MIME-Version']

        return mime_text

    def _make (self, from_, to, body, subject, attachments) :
        from_   = unicode(from_)
        to      = _Recipients(to)
        body    = unicode(body)
        subject = unicode(subject)

        try :
            attachments.__iter__
        except AttributeError :
            # <attachments> is treated as a single attachment.
            attachment  = attachments
            attachments = [attachment]
        else :
            attachments = list(attachments)

        message = email.MIMEMultipart.MIMEMultipart()

        message['From']    = str(from_)
        message['To']      = str(to)
        message['Date']    = email.Utils.formatdate(localtime=True)
        message['Subject'] = email.Header.Header(unicode(subject),
                                                 constants.ISO)

        message.attach(self._as_mime_text(body))

        for attachment in attachments :
            try :
                attachment._is_attachment
                attachment.make
            except AttributeError :
                raise AttributeError('Attachments should be instances of the '
                                     '<Attachment> class.')
            else :
                message.attach(attachment.make())

        return message

    def make (self) :
        ''' This makes and returns a MIME message object based off of the
            <email.MIMEMultipart.MIMEMultipart> class. '''

        message = self._make(self.from_, self.to, self.body, self.subject,
                             self.attachments)
        return message

class _Hist (_BaseContainer) :
    ''' This manages a historical list of objects. '''

    def __init__ (self, record=True) :
        self.set_recording(should_record=record)

        self._past = []

    def _get_container (self) :
        return self._past

    def set_recording (self, should_record) :
        ''' Should history be recorded? '''

        self._is_recording = bool(should_record)

    def is_recording (self) :
        ''' Is history currently being recorded? '''

        return self._is_recording

    def clear (self) :
        del self._past[:]

    def add (self, item) :
        if self._is_recording :
            self._past.append(item)

class EmailServer (object) :
    ''' This class manages the connection to the server. This is merely a
        facade for the <smtplib.SMTP> class.

        <host>        : The hostname.
        <port>        : The port number.
        <username>    : The username for logging into the server (not always
                        required).
        <password>    : The password for logging into the server (not always
                        required).
        <record_hist> : If this option is true, then all of the message objects
                        sent will be recorded in an iterable history object
                        (<self.hist>). '''

    _is_email_server = True

    def __init__ (self, host, port, username=None, password=None,
                  record_hist=False) :
        self.host     = host
        self.port     = port
        self.username = username
        self.password = password

        self.hist = _Hist(record=record_hist)

    def _log_in (self, server) :
        ''' This attempts to log into the server. '''

        if self.username is not None and self.password is not None :
            try :
                server.login(unicode(self.username), unicode(self.password))
            except smtplib.SMTPAuthenticationError :
                try :
                    server.login(str(self.username), str(self.password))
                except smtplib.SMTPAuthenticationError :
                    raise ValueError("Couldn't log into the server with the "
                                     'credentials given.')

        return server

    def _connect_to_server (self) :
        ''' This attempts to connect to a server. '''

        if isinstance(self.host, unicode) :
            self.host = str(self.host)

        if isinstance(self.port, unicode) :
            self.port = str(self.port)

        try :
            server = smtplib.SMTP(host=self.host, port=self.port)
        except socket.gaierror :
            raise ValueError('Failed to connect, probably a bad hostname or '
                             'port number.')
        else :
            server.starttls()

            self._log_in(server)

            return server

    def _send_individual_message (self, server, message) :
        try :
            message.from_
            message.to
            message.make
        except AttributeError :
            raise AttributeError('The <EmailServer> class can only send '
                                 '<Message> objects.')
        else :
            from_ = message.from_
            # With <list(_Recipients(message.to))>, a list is used because
            # <smtplib> treats a string as a single address (even if it
            # contains multiple valid addresses).
            to = list(_Recipients(message.to))
            literal = unicode(message)

            try :
                errors = server.sendmail(from_, to, literal)
            except smtplib.SMTPSenderRefused :
                raise
            else :
                info = (message, from_, to, literal, errors,
                        iso_time.iso_date_time())
                self.hist.add(info)

    def _test (self) :
        ''' This tests if a connection to the server can be made. This does not
            send a message, and this does not guarantee that a connection to
            the server can be reestablished in the future. If no exceptions are
            raised, it means everything went well. '''

        server = self._connect_to_server()
        server.quit()

    def send (self, messages) :
        ''' Send an individual <Message> object, or an iterable container,
            e.g., <list>, <set>, <tuple> of <Message> objects. '''

        server = self._connect_to_server()

        if hasattr(messages, '_is_message') :
            # A single message is sent.
            message  = messages
            messages = [message]

        for message in messages :
            self._send_individual_message(server, message)

        server.quit()

