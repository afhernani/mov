#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk

__author__ = 'Hernani Aleman Ferraz'
__email__ = 'afhernani@gmail.com'
__apply__ = 'Flash - player'
__version__ = '1.2'

class Over(tk.Toplevel):
    """
    call this class Over.
    first: create variable in context root
    self.vartext = tk.StringVar(value='.6')
    self.vartext.trace('w', self.trace_vartext)
    after call this way at function or
    param = {'textvariable': self.vartext}
    dialog = Over(master=self.master, cnf=param)
    dialog.mainloop()

    """
    def __init__(self, master=None, cnf={}, **kw):
        tk.Toplevel.__init__(self, master)
        self.master = master
        self.vartext = cnf['textvariable']
        self.overrideredirect(True) # sin bordes
        self.create_widgets()
        # hay que posicionarla despues que se redimensione
        self.posstcenter(self.master)
        self.wm_attributes('-alpha', 0.7)
        self.bind('<Leave>', self.mouse_leave)

    def mouse_leave(self, event):
        self.destroy()

    def posstcenter(self, toplevel):
        toplevel.update_idletasks()
        # x = toplevel.winfo_rootx()
        # y = toplevel.winfo_rooty()
        px, py = toplevel.winfo_pointerxy()
        # print(px, py)
        w = self.winfo_width()
        h = self.winfo_height()
        self.wm_overrideredirect(True)
        self.wm_geometry('+%d+%d'%(px - w, py - h))
        # print(x, y)

    def create_widgets(self):
        '''
        add scale in window toplevel
        '''
        self.scale = tk.Scale(self, from_=1, to=0, orient='vertical', resolution=0.1, 
                                sliderlength=15, width=8, command=self.onscale)
        self.scale.set(float(self.vartext.get()))
        self.scale.pack(side='top', fill='y', expand=1)

        # self.quit = tk.Button(self, text="QUIT", fg="red",
        #                      command=self.destroy)
        # self.quit.pack(side="bottom")


    def onscale(self, val):
        print(val)
        self.vartext.set(float(val))

