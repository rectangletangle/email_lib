''' This module contains relevant constants. '''


__all__ = ['ASCII', 'ISO', 'UTF', 'ENCODINGS', 'MIME_TYPE_TEXT',
           'MIME_TYPE_PNG_IMAGE', 'MIME_TYPE_JPG_IMAGE',
           'MIME_TYPE_APPLICATION', 'MIME_TYPES']

''' Some common encoding scheme names. '''
ASCII = 'us-ascii'
ISO   = 'iso-8859-1'
UTF   = 'utf8'

ENCODINGS = [ASCII, ISO, UTF]

''' Some commonly used MIME content-types, for convenience when using
    autocomplete. '''
MIME_TYPE_TEXT        = 'text/plain'
MIME_TYPE_PNG_IMAGE   = 'image/png'
MIME_TYPE_JPG_IMAGE   = 'image/jpg'
MIME_TYPE_APPLICATION = 'application/octet-stream'

MIME_TYPES = [MIME_TYPE_TEXT, MIME_TYPE_PNG_IMAGE, MIME_TYPE_JPG_IMAGE,
              MIME_TYPE_APPLICATION]

