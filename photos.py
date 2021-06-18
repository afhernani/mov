#!/usr/bin/env python3
import tkinter as tk
try:
    from PIL import Image
except ImportError:
    from pil import Image
    print('Error to load PIL lib, try: pip install pillow')
import os, sys

__author__ = 'Hernani Aleman Ferraz'
__email__ = 'afhernani@gmail.com'
__apply__ = 'Flash - player'
__version__ = '1.2'


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Photos():
    def __init__(self):
        self._apply = tk.PhotoImage(file=resource_path('Images/apply_b.png'))
        self._play = tk.PhotoImage(file=resource_path('Images/play_b.png'))
        self._pause = tk.PhotoImage(file=resource_path('Images/pause_b.png'))
        self._snapshot = tk.PhotoImage(file=resource_path('Images/snapshot_b.png'))
        self._repeat = tk.PhotoImage(file=resource_path('Images/repeat_b.png'))
        self._open = tk.PhotoImage(file=resource_path('Images/open_b.png'))
        self._volume = tk.PhotoImage(file=resource_path('Images/sound_b.png'))
        self._logo = Image.open(resource_path('Images/flash.png'))

if __name__ == '__main__':
    root = tk.Tk()
    p = Photos()
