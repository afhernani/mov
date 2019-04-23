#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk
import time
import os
from videostream import VideoStream

__version__ = '1.1'

class ScreenPlayer:
    def __init__(self, window, window_title, video_source=0):
        ''' Initialice window app '''
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.window['bg'] = 'Black'
        self.window.resizable(width=False, height=False)
        self.dirImages = ''
        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoStream(self.video_source)
        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width = self.vid.w, height = self.vid.h)
        self.canvas.pack()
        # Button that lets the user take a snapshot
        self.btn_snapshot=tk.Button(window, text="Snapshot", command=self.snapshot)
        self.btn_snapshot.pack(side='left')
        # Button open
        self.btn_open = tk.Button(window, text='...', command=self.open_file)
        self.btn_open.pack(side='right')
        # Button replay
        self.btn_replay = tk.Button(window, text=">>", command=self.replay)
        self.btn_replay.pack(side='right')
        # Button play-pausa
        self.btn_toogle_pause = tk.Button(window, text="[]", command=self.toogle_pause)
        self.btn_toogle_pause.pack(side='right')
        # Slade
        self.var_t = tk.DoubleVar()
        self.scale = tk.Scale(window, from_=0.0, to=self.vid.duration, showvalue=0, orient='horizontal', variable=self.var_t, 
                        resolution=0.1, sliderrelief='flat', command=self.onScale )
        self.scale.pack(side='left', fill='x', expand=1)
        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = self.vid.f_rate
        self.update()

        self.window.mainloop()

    def open_file(self):
        ''' Open file with menu ... '''
        dirpath = os.path.dirname(self.video_source)
        file = filedialog.askopenfile(initialdir=dirpath, title='select file', 
                                        filetypes={('mp4','*.mp4'), ('flv','*.flv')})
        print(file)
        if not file == None:
            if os.path.exists(file.name):
                self.video_source = file.name
                self.replay()
        
    def toogle_pause(self):
        if self.btn_toogle_pause['text']=='[]':
            self.btn_toogle_pause.configure(text='>')
            self.vid.toggle_pause()
        else:
            self.btn_toogle_pause.configure(text='[]')
            self.vid.toggle_pause()

    def onScale(self, val):
        print('scale onScale ->', val)
        self.vid.seek(pts=float(val))
        #self.var_t.set(v)


    def replay(self):
        ''' get replay '''
        self.vid = VideoStream(self.video_source)
        self.delay = self.vid.f_rate
        # valores de la barra.
        self.var_t.set(0.0)
        self.scale.configure(to=self.vid.duration)
        # h = self.window.winfo_reqheight()
        # w = self.window.winfo_reqwidth()
        # h_b = self.btn_open['height'] # da cero height no definida ????
        # print('boton height ->', h_b)
        h_f = int(self.vid.h + 35)
        w_f = int(self.vid.w)
        # wscale = w_f / w
        # hscale = h_f / h
        self.canvas.config(width=self.vid.w, height=self.vid.h)
        #self.window.config(width=w_f, height=h_f)
        # rescale all the objects tagged with the "all" tag
        cad = f'{w_f}x{h_f}'
        self.window.geometry(cad)

    def snapshot(self):
        '''
        Get a frame from the video source
        '''
        # Get a frame from the video source
        #frame = self.vid.get_frame()[2]
        frame = self.vid.imagen
        if frame is None:
            print('the video stream is closed')
            return
        # define options for opening
        time_str = time.strftime("%d-%m-%Y-%H-%M-%S")
        filename  = f"frame-{time_str}.jpg"
        title='Save file as'
        filetypes={('png','*.png'), ('jpg','*.jpg')}
        fileExt = '*.jpg'
        options = {}
        options['defaultextension'] = fileExt
        options['filetypes'] = filetypes
        options['initialfile'] = filename
        options['title'] = title
        if self.dirImages != '':
            options['initialdir'] = self.dirImages
        else:
            options['initialdir'] = os.getenv('HOME')
        
        filesave = filedialog.asksaveasfilename(**options)
        
        if filesave !='':
            frame.save(filesave)
            # actualiza directorio si este ha cambiado
            self.dirImages = os.path.dirname(filesave)
        #self.vid.snapshot()
        print(filesave)
        pass
 
    def update(self):
        # Get a frame from the video source
        val, pts, frame = self.vid.get_frame()

        if frame is not None:
            self.photo = ImageTk.PhotoImage(frame)
            self.canvas.delete('all') # TODO: veamos que pasa con esto....
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
            self.var_t.set(pts)

        self.window.after(self.delay, self.update)


if __name__ == '__main__':
    # Create a window and pass it to the Application object
    ScreenPlayer(tk.Tk(), "Tkinter and ffpyplayer", video_source='_Work/tem.mp4')