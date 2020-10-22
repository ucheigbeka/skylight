from sms.utils.popups import SuccessPopup


def about():
    msg = ''' Student Management System
    '''
    SuccessPopup(msg, title='Project Skylight', auto_dismiss=False)
