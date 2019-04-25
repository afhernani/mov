#!/usr/bin/env python3
from tkinter import *

class Photos():
    def __init__(self):
        self._play = PhotoImage(file='Images/play_b.png')
        self._pause = PhotoImage(file='Images/pause_b.png')
        self._snapshot = PhotoImage(file= 'Images/snapshot_b.png')
        self._repeat = PhotoImage(file='Images/repeat_b.png')
        self._open = PhotoImage(file='Images/open_b.png')

