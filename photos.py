#!/usr/bin/env python3
from tkinter import *
import os

class Photos():
    def __init__(self):
        self.dirname = os.path.abspath(__file__)
        print(self.dirname)
        self.dirname = os.path.dirname(self.dirname)
        print(self.dirname)
        self._apply = PhotoImage(file=os.path.join(self.dirname, 'Images/apply_b.png'))
        self._play = PhotoImage(file=os.path.join(self.dirname, 'Images/play_b.png'))
        self._pause = PhotoImage(file=os.path.join(self.dirname, 'Images/pause_b.png'))
        self._snapshot = PhotoImage(file=os.path.join(self.dirname, 'Images/snapshot_b.png'))
        self._repeat = PhotoImage(file=os.path.join(self.dirname, 'Images/repeat_b.png'))
        self._open = PhotoImage(file=os.path.join(self.dirname, 'Images/open_b.png'))


if __name__ == '__main__':
    root = Tk()
    p = Photos()
