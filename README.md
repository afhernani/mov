# TKINTER WITH FFPYPLAYER ONLY
## Requerimientos.
### Inatalation
    On windows 7+ (64 or 32 bit) and linux (64 bit), ffpyplayer wheels can be installed for python 3.5+ using:
    pip install ffpyplayer
    Instalation and documentation at (ffpyplayer)[https://matham.github.io/ffpyplayer/installation.html]
#### Others packages.
     Pillow, tkinter
## Version development.
    Version = 1.0
### Advantage:
    Good sound and image synchronization. 
    Use of standard GUI python tkinter library
    Resized automatic main window according to video format.
    Simple example of a video editor.
### Disadvantages:
    main window not resizable at the user's will.
    It does not have time scroll bars or sound control.
    lack of more buttons and more obtions, pause, stop, play, etc ...
### Improvements:
    Adapt the image buffer to the size of the form with custom resizing.
    add time and sound controls, with inter-activity locks.
    many other things that must be developed.
## Version development.
    Version = 1.1
### Improvements:
    included scroll bar and buttons pause and restart and snapshot
    start of the application without a source file, and resizing of
    image when we act with the main window.
## Version development.
    Version = 1.2
### Improvements:
    - Avoid the reproduction of the distorted image, maintaining its 
    scale proportion.
    - Others ...
# Create exe with pyinstaller:

- creamos el fichero spec para la compilacion como sigue:

`pyi-makespec --onefile --icon=./pirate-10.ico viewerplayer.py`

- hacemos las modificaciones en el fichero viewerplayer.spec y compilamos como sigue:

`pyinstaller --onefile viewerplayer.spec`

viewerplayer.spce

```
# -*- mode: python ; coding: utf-8 -*-


block_cipher = None

site_packages = '/home/hernani/.local/lib/python3.8/site-packages'
image_root = '/home/hernani/Documentos/Documentos/python/github.com/mov-v1.2/Images'

a = Analysis(['viewerplayer.py'],
             pathex=['/home/hernani/Documentos/Documentos/python/github.com/mov-v1.2'],
             binaries=[
                 ('{}/ffpyplayer/*.so'.format(site_packages), 'ffpyplayer'),
                 ('{}/ffpyplayer/player/*.so'.format(site_packages), 'ffpyplayer/player')
             ],
             datas=[],
             hiddenimports=['PIL', 'PIL._tkinter_finder'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += [('apply_b.png','{}/apply_b.png'.format(image_root), "DATA"), ('flash.png', '{}/flash.png'.format(image_root), "DATA"), ('open_b.png', '{}/open_b.png'.format(image_root), "DATA"), ('pause_b.png', '{}/pause_b.png'.format(image_root), "DATA"), ('play_b.png', '{}/play_b.png'.format(image_root), "DATA"), ('repeat_b.png', '{}/repeat_b.png'.format(image_root), "DATA"), ('snapshot_b.png', '{}/snapshot_b.png'.format(image_root), "DATA"), ('sound_b.png', '{}/sound_b.png'.format(image_root), "DATA")]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='viewerplayer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True , icon='pirate-10.ico')

```
