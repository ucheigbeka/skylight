# -*- mode: python ; coding: utf-8 -*-

import os
from kivy_deps import sdl2, glew

block_cipher = None

kv_imports_path = os.path.join('sms', 'forms', 'kv_container', 'imports.kv')
output_path = os.path.join('sms', 'utils')
paths, sep = [], os.sep
count = 2
with open(kv_imports_path) as fd:
    for line in fd.readlines():
        if line.startswith('#:import'):
            if count:
                # Eliminates the os and Windows imports
                count -= 1
                continue
            mod = line.strip('\n').split()[-1]
            mod_list = mod.split('.')[:-1]
            mod_list[-1] += '.py'
            path = sep.join(mod_list)
            if path not in paths:
                paths.append(path)

add_paths = list(zip(paths, [output_path] * len(paths)))

# Additional resources
add_paths.append(('README.md', '.'))
add_paths.append(('skylight.png', '.'))
add_paths.append(('next_release.txt', '.'))
add_paths.append(('copyright.txt', '.'))


a = Analysis(['main.py'],
             pathex=['C:\\Users\\uche\\Documents\\GitHub\\skylight'],
             binaries=[],
             datas=[*add_paths],
             hiddenimports=[],
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
