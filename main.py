import sys
import traceback

with open('logs.txt', 'w') as fd:
    sys.stderr = fd

    try:
        from run import StudentManagementSystemApp
        StudentManagementSystemApp().run()
    except Exception:
        traceback.print_exc(file=fd)
