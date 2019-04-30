#!/usr/bin/env python3
import tkinter as tk
from PIL import Image
import os

__author__ = 'Hernani Aleman Ferraz'
__email__ = 'afhernani@gmail.com'
__apply__ = 'Flash - player'
__version__ = '1.2'

class Photos():
    def __init__(self):
        self.dirname = os.path.abspath(__file__)
        print(self.dirname)
        self.dirname = os.path.dirname(self.dirname)
        print(self.dirname)
        self._apply = tk.PhotoImage(file=os.path.join(self.dirname, 'Images/apply_b.png'))
        self._play = tk.PhotoImage(file=os.path.join(self.dirname, 'Images/play_b.png'))
        self._pause = tk.PhotoImage(file=os.path.join(self.dirname, 'Images/pause_b.png'))
        self._snapshot = tk.PhotoImage(file=os.path.join(self.dirname, 'Images/snapshot_b.png'))
        self._repeat = tk.PhotoImage(file=os.path.join(self.dirname, 'Images/repeat_b.png'))
        self._open = tk.PhotoImage(file=os.path.join(self.dirname, 'Images/open_b.png'))
        self._volume = tk.PhotoImage(file=os.path.join(self.dirname, 'Images/sound_b.png'))
        self._logo = Image.open(os.path.join(self.dirname, 'Images/flash.png'))

if __name__ == '__main__':
    root = tk.Tk()
    p = Photos()
