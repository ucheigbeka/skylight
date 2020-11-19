from sms.utils.popups import SuccessPopup


def about():
    msg = ''' Student Management System
    
    Feedback Icon made by Those Icons from www.flaticon.com"
    '''
    about_popup = SuccessPopup(msg, title='Project Skylight', auto_dismiss=False)
    about_popup.size_hint = (.4, .27)
    about_popup.open()
