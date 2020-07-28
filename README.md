# Skylight
This project represents the client side of the **Student Management System** for the Department of Mechanical Engineering, University of Benin.

## To run on linux
Check out the [official kivy documentations](https://kivy.org/doc/stable/installation/installation-linux.html) to install kivy on Linux 

+ Then install dependencies with ```pip3 install -r requirements-linux.txt```
+ Run the app with `python3 run.py`

## Instructions For Compilation
* **Pyinstaller 3.1+** is required for compiling the source code into an executable file (.exe for Windows). The same instructions apply to bundling for Windows, Mac OS X and GNU/Linux. Pyinstaller should be installed using pip:
```
    python -m pip install pyinstaller
```

* [UPX](https://upx.github.io/) is also recommended but not required. It is a free utility that significantly compresses the executable. You can download the latest version for your os [here](https://github.com/upx/upx/releases/). After installation, make sure that `upx.exe` is [available in your `$PATH` environment variable](https://www.java.com/en/download/help/path.xml).

* Execute the spec file in your terminal
```
    pyinstaller sms.spec
```
or to avoid the prompt for modifying the dist folder if it already exists, execute the spec file with the `--noconfirm` flag.
```
    pyinstaller --noconfirm sms.spec
```

* Pyinstaller creates 2 folders, a build and dist folder. The bundled app can be found in the dist folder.
