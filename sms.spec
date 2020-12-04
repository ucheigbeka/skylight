# -*- mode: python ; coding: utf-8 -*-

import os
import glob
from kivy_deps import sdl2, glew

block_cipher = None

base_dir = os.getcwd()
kv_imports_path = os.path.join('sms', 'forms', 'kv_container', 'imports.kv')

# Additional resources
add_paths = []
add_paths.append(('README.md', '.'))
add_paths.append(('skylight.png', '.'))
add_paths.append(('next_release.txt', '.'))
add_paths.append(('copyright.txt', '.'))
add_paths.append(('.version', '.'))

# Hidden imports
hidden_imports, exceptions = [], ['template', 'signin', 'os', 'kivy.core.window']

## hidden kv imports
with open(kv_imports_path) as fd:
    for line in fd.readlines():
        if line.startswith('#:import'):
            cls = line.strip('\n').split()[-1]
            mod = cls[: cls.rfind('.')] if '.' in cls else cls
            if mod not in exceptions and mod not in hidden_imports:
                hidden_imports.append(mod)

## hidden py imports - forms
for form in os.listdir(os.path.join(base_dir, 'sms', 'forms')):
    module, ext = os.path.splitext(form)
    if ext == '.py' and module not in exceptions:
        hidden_imports.append('sms.forms.' + module)

## hidden py imports - fragments
for frag in os.listdir(os.path.join(base_dir, 'sms', 'forms', 'fragments')):
    module, ext = os.path.splitext(frag)
    if ext == '.py' and module not in exceptions:
        hidden_imports.append('sms.forms.fragments.' + module)

a = Analysis(['main.py'],
             pathex=['C:\\Users\\uche\\Documents\\GitHub\\skylight'],
             binaries=[],
             datas=[*add_paths],
             hiddenimports=hidden_imports,
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='sms',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='icon.ico')
coll = COLLECT(exe, Tree('sms', excludes=['*.py', '__pycache__'], prefix='sms'),
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
               upx=True,
               upx_exclude=['vcruntime140.dll'],
               name='sms')
