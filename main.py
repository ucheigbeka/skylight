import sys

with open('logs.txt', 'w') as fd:
    sys.stderr = fd

    from run import StudentManagementSystemApp

    StudentManagementSystemApp().run()
