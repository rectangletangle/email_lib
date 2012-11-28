''' This module contains the classes and functions which handle the user
    interface (a command-line interface). '''


import sys
import getpass
import mimetypes

import email_lib

__all__ = ['cli']

class CLI (object) :
    ''' A command-line interface class, this allows the user to send a single
        message per run. '''

    def __init__ (self, intro=None, ask_mime_type=False, record_hist=True) :
        if intro is None :
            text = ' Email Library %s CLI ' % email_lib.__version__
            intro = self._center(text)

        self.intro = intro
        self.ask_mime_type = ask_mime_type
        self.record_hist = record_hist

    def _yes_to (self, message='', default_to_yes=True) :
        if message :
            message += ' '

        affirmative = {'y', 'yes', 'true', 'ja'}
        negative    = {'n', 'no', 'false', 'nein'}

        if default_to_yes :
            yn = '(y/n) : '
            affirmative.add('')
        else :
            yn = '(n/y) : '
            negative.add('')

        while True :
            reply = raw_input(message + yn).strip().lower()

            if reply in affirmative :
                return True
            elif reply in negative :
                return False
            else :
                continue

    def _center (self, string, width=80, decor='_') :
        width -= len(string)

        if width < 0 :
            # No room for a border
            return string

        half = width // 2
        first_half  = half
        second_half = half

        if width % 2 != 0 : # If the width is odd
            second_half += 1

        return (decor * first_half) + string + (decor * second_half)

    def _indent (self, string, tabs=1) :
        return ('\t' * tabs) + ('\n' + ('\t' * tabs)).join(string.splitlines())

    def _get_server_info (self) :
        host = raw_input('Hostname : ')
        port = raw_input('Port Number : ')

        try :
            sys.stdin.isatty
        except AttributeError :
            input_func = getpass.getpass
        else :
            if sys.stdin.isatty() :
                # This hides the password for GUI mode.
                input_func = getpass.getpass
            else :
                # <raw_input> may cause security issues here.
                input_func = raw_input

        username = input_func('Username (if necessary) : ') or None
        password = input_func('Password (if necessary) : ') or None

        return (host, port, username, password)

    def _get_message_info (self) :
        from_ = raw_input('From Address : ')

        to = []
        while True :
            recipient = raw_input('Recipient Address : ')
            to.append(recipient)

            if not self._yes_to('Add another recipient?') :
                break

        subject = raw_input('Subject : ')

        while True :
            message_path = raw_input('Message Body File Name : ')

            try :
                with open(message_path, 'r') as f :
                    body = f.read()
            except IOError :
                print 'The file <%s> was not found.' % message_path
                continue
            else :
                break

        return (from_, to, subject, body)

    def _get_attachments (self) :
        attachments = []
        while True :
            path = raw_input('Attachment File Name : ')
            read_mode = raw_input('Read Mode (plain/binary) : ')

            if self.ask_mime_type :
                type_ = raw_input('MIME content-type : ') or None
            else :
                guessed_type = mimetypes.guess_type(path)[0]
                if guessed_type is None :
                    type_ = raw_input('MIME content-type : ')
                else :
                    type_ = guessed_type

            attachment = email_lib.Attachment(path, read_mode, type_)
            attachments.append(attachment)

            if not self._yes_to('Add another attachment?') :
                break

        return attachments

    def _print_message_info (self, from_, to, subject, body, attachments) :
        ''' This prints out the message's information, for verification
            purposes. '''

        if len(to) == 0 :
            to_str = ''
        elif len(to) == 1 :
            to_str = to[0]
        else :
            to_str = '<' + ', '.join(to) + '>'

        print 'From    : %s' % from_
        print 'To      : %s' % to_str
        print 'Subject : %s' % subject
        print 'Body    : '
        if body :
            print self._indent(body)

        if attachments :
            print 'Attachments : '
            print self._indent('\n'.join(att.path for att in attachments))

    def _try_to_send (self, server, message) :
        while True :
            print 'Sending...'
            try :
                server.send(message)
            except :
                if not self._yes_to('Failed to send the message, would you '
                                    'like to try again?') :
                    print 'Message canceled'
                    break
            else :
                print 'Message sent successfully'
                break

    def run (self) :
        ''' This runs the CLI, so that it can gather input from the user. '''

        print self.intro
        print

        host, port, username, password = self._get_server_info()

        from_, to, subject, body = self._get_message_info()

        if self._yes_to('Do you want to add attachments?') :
            attachments = self._get_attachments()
        else :
            attachments = []

        message = email_lib.Message(from_, to, subject, body, attachments)

        server = email_lib.EmailServer(host, port, username, password,
                                       self.record_hist)

        print self._center(' Message ')
        self._print_message_info(from_, to, subject, body, attachments)
        print '_' * 80

        if self._yes_to('Send the message?') :
            self._try_to_send(server, message)
        else :
            print 'Message canceled'

        return list(server.hist)

def cli (*args, **kw) :
    ''' This prompts the user for input, then sends a single email message
        constructed from that input.

        Note : This function should probably only be called within a try block
               with a <KeyboardInterrupt> exception, because occasionally those
               do arise. '''

    cli = CLI(*args, **kw)
    return cli.run()

def __run__ (print_hist=False, *args, **kw) :
    ''' This is almost the same as the <cli> function, however this handles
        system exit codes. When called, this will basically act as a standalone
        command-line program. '''

    try :
        hist = cli(*args, **kw)
    except KeyboardInterrupt :
        print
        sys.exit(1)
    except :
        raise
        sys.exit(1)
    else :
        if print_hist :
            print 'History : '
            for info in hist :
                print '/t', info

        sys.exit(0)

if __name__ == '__main__' :
    __run__()

