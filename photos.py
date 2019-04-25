#!/usr/bin/env python3
import tkinter as tk
import os

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


if __name__ == '__main__':
    root = tk.Tk()
    p = Photos()
