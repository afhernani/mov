#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk
import time
import os
from videostream import VideoStream
from photos import Photos

__author__ = 'Hernani Aleman Ferraz'
__email__ = 'afhernani@gmail.com'
__version__ = '1.1'

class ScreenPlayer:
    def __init__(self, window, window_title, video_source=None):
        ''' Initialice window app '''
        self.window = window
        self.window.title(window_title)
        self.window['bg'] = 'Black'
        self.window.resizable(width=False, height=False)
        self.photo = None
        self.photos = Photos()
        # self.window.call('wm', 'iconphoto', self.window, self.photos._apply)
        self.soundvar = tk.DoubleVar(value=0.3)
        self.window.wm_iconphoto(True, self.photos._apply)
        self.dirImages = '.'
        self.video_source = video_source
        w = 350; h = 230; pts = 100.0
        self.active_scale = False
        self.vid = None
        if self.video_source is not None:
            # open video source (by default this will try to open the computer webcam)
            try:
                self.vid = VideoStream(self.video_source)
                w = self.vid.w
                h = self.vid.h
                pts = self.vid.duration
                self.soundvar.set(self.vid.player.get_volume())
            except Exception as e:
                print(e)
                self.vid = None
        # event changed de volume
        self.soundvar.trace('w', self.soundvar_adjust)
        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width = w, height = h)
        self.canvas.pack()
        # Button that lets the user take a snapshot
        self.btn_snapshot=tk.Button(window, text="Snapshot", command=self.snapshot)
        self.btn_snapshot['image'] = self.photos._snapshot 
        self.btn_snapshot.pack(side='left')
        # Button open
        self.btn_open = tk.Button(window, text='...', command=self.open_file)
        self.btn_open['image'] = self.photos._open
        self.btn_open.pack(side='right')
        # button volum
        self.btn_volume = tk.Button(window, text='volume', command=self.open_adjust_volumen)
        self.btn_volume['image'] = self.photos._volume
        self.btn_volume.pack(side='right')
        # Button replay
        self.btn_replay = tk.Button(window, text=">>", command=self.replay)
        self.btn_replay['image'] = self.photos._repeat
        self.btn_replay.pack(side='right')
        # Button play-pausa
        self.btn_toogle_pause = tk.Button(window, text="[]", command=self.toogle_pause)
        self.btn_toogle_pause['image'] = self.photos._pause
        self.btn_toogle_pause.pack(side='right')
        # Slade
        self.var_t = tk.DoubleVar()
        self.scale = tk.Scale(window, from_=0.0, to= pts, showvalue=0, orient='horizontal', variable=self.var_t, 
                        resolution=0.2, sliderrelief='flat', command=self.onScale )
        self.scale.pack(side='left', fill='x', expand=1)
        self.delay = 16
        if self.video_source is not None:
            # After it is called once, the update method will be automatically called every delay milliseconds
            self.delay = self.vid.f_rate
            self.btn_toogle_pause['image'] = self.photos._play
        else:
            self.canvas.create_image(0, 0, image = self.photos._logo, anchor = tk.NW)
            self.canvas.configure(width = self.photos._logo.width(),
                                    height=self.photos._logo.height())
        self.val = None
        self.pts = None
        self.update()
        self.window.mainloop()
    
    def open_adjust_volumen(self):
        from overpanel import Over
        param = {'textvariable': self.soundvar}
        dialog = Over(master=self.window, cnf=param)
        dialog.mainloop()
        pass
    
    def soundvar_adjust(self, *args):
        print('sound adjust ->', self.soundvar.get())
        if self.vid:
            print('if self.vid:')
            self.vid.player.set_volume(float(self.soundvar.get()))

    def isurl(self, tip=None):
        '''
        Return bolean true si existe and it's ends with
        ('.mp4', '.MP4', '.flv', '.FLV', '.mpg', '.avi')
        '''
        if not tip:
            return False
        exten = ('.mp4', '.MP4', '.flv', '.FLV', '.mpg', '.avi')
        if os.path.exists(tip):
            if source.endswith(exten):
                return True
        return False

    def open_file(self):
        ''' Open file with menu ... '''
        if not self.video_source:
            dirpath='.'
        else:
            dirpath = os.path.dirname(self.video_source)
        file = filedialog.askopenfile(initialdir=dirpath, title='select file', 
                                        filetypes={('flv','*.flv'), ('mp4','*.mp4'),
                                        ('avi','*.avi'), ('mpg','*.mpg')}, 
                                        defaultextension='*.mp4')
        print(file)
        if not file == None:
            if os.path.exists(file.name):
                self.video_source = file.name
                self.newplay()
        
    def toogle_pause(self):
        '''
        toogle pause
        '''
        if not self.vid:
            return
        if self.val =='paused':
            self.btn_toogle_pause['image'] = self.photos._play
            self.vid.toggle_pause()
        else:
            self.btn_toogle_pause['image'] = self.photos._pause
            self.vid.toggle_pause()

    def onScale(self, val):
        # print('scale onScale ->', val)
        if not self.vid:
            return
        try:
            self.active_scale = False
            self.vid.seek(pts=float(val))
            self.active_scale = True
        except Exception as e:
            print(e)
            self.active_scale = True
        # self.var_t.set(v)

    def replay(self):
        if not self.vid:
            return
        if self.val == 'paused':
            self.vid.seek(pts=0.01)
            self.vid.toggle_pause()
        else:
            self.vid.seek(pts=0.01)
        pass

    def newplay(self):
        ''' get replay '''
        self.btn_toogle_pause['image'] = self.photos._play
        self.vid = VideoStream(self.video_source)
        self.delay = self.vid.f_rate
        # valores de la barra.
        self.var_t.set(0.0)
        self.scale.configure(to=self.vid.duration)
        # ajuste valores de sonido al nivel seleccionado.
        if self.soundvar.get() == 0.3: # reference value
            self.soundvar.set(self.vid.player.get_volume())
        else:
            self.vid.player.set_volume(float(self.soundvar.get()))
        # dimension vertical ventana.
        h = self.btn_open.winfo_height()
        h_f = int(self.vid.h + h)
        w_f = int(self.vid.w)
        self.canvas.config(width=self.vid.w, height=self.vid.h)
        # rescale all the objects tagged with the "all" tag
        cad = f'{w_f}x{h_f}'
        self.window.geometry(cad)

    def snapshot(self):
        '''
        Get a frame from the video source
        '''
        # Get a frame from the video source
        #frame = self.vid.get_frame()[2]
        if not self.vid:
            return
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
        if not self.vid:
            self.window.after(self.delay, self.update)
            return
        self.val, self.pts, frame = self.vid.get_frame()

        if frame is not None:
            self.photo = ImageTk.PhotoImage(frame)
            self.canvas.delete('all') # TODO: veamos que pasa con esto....
            self.canvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
            if not self.active_scale:
                self.var_t.set(self.pts)

        self.window.after(self.delay, self.update)


if __name__ == '__main__':
    # Create a window and pass it to the Application object
    source = '/media/hernani/WDatos/Share/afhernani.com/embed/_Work/dw11222.mp4'
    ScreenPlayer(tk.Tk(), "Tkinter and ffpyplayer", video_source=None)