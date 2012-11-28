'''
    Email Library (email_lib)

    Version  : 0.0
    Language : Python 2.7.3
    Date     : 2012-11-28
    Author   : Drew A. French

    License Statement :
        Simplified BSD License

        Copyright (c) 2012, Drew A. French
        All rights reserved.

        Redistribution and use in source and binary forms, with or without
        modification, are permitted provided that the following conditions are
        met:

        1. Redistributions of source code must retain the above copyright
           notice, this list of conditions and the following disclaimer.
        2. Redistributions in binary form must reproduce the above copyright
           notice, this list of conditions and the following disclaimer in the
           documentation and/or other materials provided with the distribution.

        THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
        "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
        LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
        PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
        OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
        SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
        LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
        DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
        THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
        (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
        OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

        The views and conclusions contained in the software and documentation
        are those of the authors and should not be interpreted as representing
        official policies, either expressed or implied, of the FreeBSD Project.

    Purpose :
            This package provides a simple and straightforward way to
        programmatically send emails with Python. The main classes in this
        package are high-level abstractions of Python's <smtplib> and <email>
        libraries.

    Features :
	   * A simple and intuitive way to send email messages
	   * Arbitrary files can easily be attached to messages
       * Messages use proper MIME headers
	   * Messages can contain unicode characters
       * An easy to use (and automate) command-line interface
'''


__version__ = '0.0'

__all__ = ['MIME_TYPE_TEXT', 'MIME_TYPE_PNG_IMAGE', 'MIME_TYPE_JPG_IMAGE',
           'MIME_TYPE_APPLICATION', 'Attachment', 'Message', 'EmailServer',
           'cli']

from email_lib.constants import (MIME_TYPE_TEXT,
                                 MIME_TYPE_PNG_IMAGE,
                                 MIME_TYPE_JPG_IMAGE,
                                 MIME_TYPE_APPLICATION)

from email_lib.lib import (Attachment,
                           Message,
                           EmailServer)

from email_lib.ui import (cli)

