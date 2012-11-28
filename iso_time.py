''' This module contains functions which return ISO 8601 formatted time
    strings. '''


import time

__all__ = ['iso_date_time', 'iso_date', 'iso_time']

ISO_DATE_CODE = '%Y-%m-%d'
ISO_TIME_CODE = '%H:%M:%S %Z'

def iso_date_time () :
    ''' This returns the date and time (as a unicode string) in ISO 8601
        format. '''

    return unicode(time.strftime('%s %s' % (ISO_DATE_CODE, ISO_TIME_CODE)))

def iso_date () :
    ''' This returns the date (as a unicode string) in ISO 8601 format. '''

    return unicode(time.strftime(ISO_DATE_CODE))

def iso_time () :
    ''' This returns the time (as a unicode string) in ISO 8601 format. '''

    return unicode(time.strftime(ISO_TIME_CODE))

def __demo__ () :
    print iso_date_time()
    print iso_date()
    print iso_time()

if __name__ == '__main__' :
    __demo__()

