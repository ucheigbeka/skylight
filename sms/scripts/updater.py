import os
import shutil
import subprocess
from zipfile import ZipFile

from sms import urlTo, AsyncRequest
from sms.setup import PROJECT_ROOT, TEMP_DIR
from sms.utils.popups import ErrorPopup, YesNoPopup


def download_upgrade():
    url = urlTo('download_fe')
    AsyncRequest(url, on_success=extract, on_failure=show_error)


def extract(resp):
    filepath = os.path.join(os.path.expanduser('~'), 'sms.zip')
    if os.path.exists(filepath): os.unlink(filepath)
    output_dir = os.path.join(os.path.expanduser('~'), 'sms_temp')
    shutil.rmtree(output_dir, ignore_errors=True)
    os.makedirs(output_dir, exist_ok=True)

    with open(filepath, 'wb') as fd:
        fd.write(resp.content)
    try:
        with ZipFile(filepath) as zf:
            zf.extractall(output_dir)
    except Exception as e:
        show_error()
        return

    # copy server config
    config_path = os.path.join(PROJECT_ROOT, 'config.json')
    if os.path.exists(config_path):
        shutil.copyfile(config_path, os.path.join(output_dir, 'config.json'))

    YesNoPopup('Click "Yes" to restart with the new version', on_yes=restart, title='Updater')


def restart():
    restarter_path = os.path.join(PROJECT_ROOT, 'restarter.bat')
    temp_restarter_path = os.path.join(TEMP_DIR, 'sms_restarter.bat')
    shutil.rmtree(temp_restarter_path, ignore_errors=True)
    shutil.copyfile(restarter_path, temp_restarter_path)
    updater_logs_path = os.path.join(os.path.expanduser('~'), 'sms_updater_logs.txt')
    subprocess.run([temp_restarter_path, '>>', updater_logs_path])


def show_error():
    ErrorPopup('Something went wrong while updating')
