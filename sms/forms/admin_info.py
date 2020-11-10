from sms.forms.template import FormTemplate
from sms.forms.fragments.admin_info import AdminInfo


class Info(FormTemplate, AdminInfo):
    title = 'Admin Info'
