#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox
try:
    from PIL import ImageTk, Image
except ImportError:
    from pil import ImageTk, Image
import time
import os
from videostream import VideoStream
from photos import Photos
from utility import proportional_resizing
from utility import image_adjustment
import configparser

__author__ = 'Hernani Aleman Ferraz'
__email__ = 'afhernani@gmail.com'
__apply__ = 'Flash - player'
__version__ = '1.2'

class ScreenPlayer(tk.Frame):
    
    def __init__(self, master=None, title=None, video=None):
        ''' Initialice window app '''
        super().__init__(master)        
        self.master = master
        # self.master.geometry('422x624+629+231') -> desarrollo ahead.
        self.pack(fill=tk.BOTH, expand=1)
        self.master.title(title)
        self.master['bg'] = 'Black'
        self.master.protocol('WM_DELETE_WINDOW', self.confirmExit)
        self.setingfile = 'flash_seting.ini'
        # self.window.resizable(width=False, height=False)
        self.n_size = None
        self.photo = None
        self.photos = Photos()
        # self.master.call('wm', 'iconphoto', self.master, self.photos._apply)
        self.soundvar = tk.DoubleVar(value=0.9)
        self.master.wm_iconphoto(True, self.photos._apply)
        self.dirImages = None
        self.dirpathmovies = tk.StringVar()  # directorio path video
        self.video_source = video
        w = 350; h = 230; self.duracion = 100.0
        self.active_scale = False
        self.vid = None
        self.val = 'paused'
        if self.video_source is not None:
            # open video source (by default this will try to open the computer webcam)
            try:
                self.dirpathmovies.set(os.path.dirname(self.video_source))
                self.vid = VideoStream(self.video_source)
                # w_f, h_f = self.vid.w, self.vid.h
                self.duracion = self.vid.duration
                
                self.soundvar.set(self.vid.player.get_volume())
                frame = None
                while frame is None:
                    self.val, self.pts, frame = self.vid.get_frame()
                size = frame.get_size()
                arr = frame.to_memoryview()[0] # array image
                self.imagen = Image.frombytes("RGB", size, arr.memview)
                w_f, h_f = self.imagen.size
                self.delay = self.vid.f_rate
                self.vid.toggle_pause()
                self._wxh = (w_f, (h_f + 40))
                self._twh = (300, 300)
            except Exception as e:
                print(e)
                self.video_source = None
        else:
            self.imagen = self.photos._logo
            w_f, h_f = self.imagen.size
            self.delay = 16
            self._wxh = (422, 624)
            self._twh = (629, 231)
            pass
        # ajuste ventana.
        str_window = str(self._wxh[0])+ 'x'+str(self._wxh[1])+ '+' + str(self._twh[0])+ '+' + str(self._twh[1])
        self.master.geometry(str_window)
        print('str ventana de inicio:', str_window)
        # event changed de volume
        self.soundvar.trace('w', self.soundvar_adjust)
        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(self, bg='red')
        # contenedor de controles
        self.conten_controls = tk.LabelFrame(self, height=4)
        # Button that lets the user take a snapshot
        self.btn_snapshot=tk.Button(self.conten_controls, text="Snapshot", command=self.snapshot)
        self.btn_snapshot['image'] = self.photos._snapshot 
        self.btn_snapshot.pack(side='left')
        # Button open
        self.btn_open = tk.Button(self.conten_controls, text='...', command=self.open_file)
        self.btn_open['image'] = self.photos._open
        self.btn_open.pack(side='right')
        # button volum
        self.btn_volume = tk.Button(self.conten_controls, text='volume', command=self.open_adjust_volumen)
        self.btn_volume['image'] = self.photos._volume
        self.btn_volume.pack(side='right')
        # Button replay
        self.btn_replay = tk.Button(self.conten_controls, text=">>", command=self.replay)
        self.btn_replay['image'] = self.photos._repeat
        self.btn_replay.pack(side='right')
        # Button play-pausa
        self.btn_toogle_pause = tk.Button(self.conten_controls, text="[]", command=self.toogle_pause)
        self.btn_toogle_pause['image'] = self.photos._play
        self.btn_toogle_pause.pack(side='right')
        # Slade
        self.var_t = tk.DoubleVar()
        self.scale = tk.Scale(self.conten_controls, from_=0.0, to= self.duracion, showvalue=0, orient='horizontal', variable=self.var_t, 
                        resolution=0.3, sliderrelief='flat', command=self.onScale )
        self.scale.pack(side='left', fill='x', expand=1)
        self.scale.bind('<ButtonPress-1>', self.scale_button_press)
        self.scale.bind('<ButtonRelease-1>', self.scale_button_release)
        self.master.bind('<Configure>', self.master_on_resize)
        # self.master.bind_all('<ButtonPress-1>', self.master_button_press)
        # self.master.bind('<ButtonRelease-1>', self.master_button_release)
        # self.master.wm_withdraw()
        self.canvas.pack(side =tk.TOP, fill=tk.BOTH, expand=1)
        self.conten_controls.pack(side='bottom', fill='x')
        
        
        if self.video_source is not None:
            self.scale.configure(to=self.duracion)
            self.btn_toogle_pause['image'] = self.photos._pause
            self.vid.player.set_volume(float(self.soundvar.get()))
            self.canvas_tags = None
            
        self.photo = ImageTk.PhotoImage(self.imagen)
        self.canvas.configure(width = w_f, height=h_f)
        self.canvas.create_image(w_f/2, h_f/2, image = self.photo, 
                                        anchor='center', tags='img')
        self.val = None
        self.pts = None
        #
        
      
        if self.video_source is None:
            self.get_init_status()
        self.update()
        self.master.mainloop()

    
    def get_init_status(self):
        '''
        extract init status of app
        Return:
        '''
        if not os.path.exists(self.setingfile):
            return
        config = configparser.RawConfigParser()
        config.read(self.setingfile)
        dirpathmovies = config.get('Setings', 'path_movies')
        if os.path.exists(dirpathmovies):
            self.dirpathmovies.set(dirpathmovies)
            # inicializa la lista con directorio duardao
        dirpathimages =config.get('Setings', 'path_images')
        if os.path.exists(dirpathimages):
            self.dirImages = dirpathimages
            # inicializa la lista con directorio duardao
    
    def set_init_status(self):
        '''
        write init status of app
        Return:
        '''
        config = configparser.RawConfigParser()
        config.add_section('Setings')
        config.set('Setings', 'path_movies', self.dirpathmovies.get())
        config.set('Setings', 'path_images', self.dirImages)
        with open(self.setingfile, 'w') as configfile:
            config.write(configfile)
        print('Write config file')

    def confirmExit(self):
        if messagebox.askokcancel('Quit', 'Are you sure you want to exit?'):
            self.master.quit()
        self.set_init_status()
        print('end process')

    def master_button_press(self, event):
        print('>> master_button_press')

    def master_button_release(self, event):
        print('>> master_button_release')

    def master_on_resize(self, event):
        _ventana = event.widget
        print(_ventana)
        widget_size =(_ventana.winfo_width(), _ventana.winfo_height() )
        if str(_ventana) == '.!screenplayer.!canvas':
            print('>> canvas:')
        m_wxh = (event.x, event.y)
        print('>> rezise:', m_wxh, self._wxh, 'widget_size:', widget_size)
        if self._wxh != m_wxh and str(_ventana) == '.!screenplayer.!canvas' and m_wxh == (0, 0):
            print('>> on_resize_master ')
            self._wxh = widget_size
            # self.master.configure(width=m_wxh[0], height=m_wxh[1])
            h_c = self.conten_controls.winfo_height()
            w = m_wxh[0] -2
            h = m_wxh[1] - h_c -2
            self.canvas.configure(width=w, height=h)
            # si es nulo self.vid or self.imagen is not None or self.vid.player.get_pause()
            # print('wm_withdraw: ', self.master.wm_withdraw())
            if self.vid is None or self.val =='paused':               
                w = self.canvas.winfo_width()
                h = self.canvas.winfo_height()
                if w <= 0 or h <= 0:
                    return
                self.canvas.delete(tk.ALL) # borra todos los objetos con ese tags....
                #  w_i, h_i = self.imagen.size
                marco = w, h  # marco de ventana
                self.imagen_copy = self.imagen.copy()
                self.imagen_copy = image_adjustment(self.imagen_copy, marco)
                self.photo = ImageTk.PhotoImage(self.imagen_copy)
                self.canvas.create_image(w/2, h/2, anchor='center', image = self.photo, tags='img')
            
    def scale_button_press(self, event):
        print('>> scale_button_press')
        self.active_scale = True
    
    def scale_button_release(self, event):
        print('>> scale_button_release')
        self.active_scale = False
    
    def open_adjust_volumen(self):
        from overpanel import Over
        param = {'textvariable': self.soundvar}
        dialog = Over(master=self.master, cnf=param)
        dialog.mainloop()
    
    def soundvar_adjust(self, *args):
        print('sound adjust ->', self.soundvar.get())
        if self.vid:
            print('if self.vid: soundvar_adjust')
            self.vid.player.set_volume(self.soundvar.get())

    def isurl(self, tip=None):
        '''
        Return bolean true si existe and it's ends with
        ('.mp4', '.MP4', '.flv', '.FLV', '.mpg', '.avi')
        '''
        if not tip:
            return False
        exten = ('.mp4', '.MP4', '.flv', '.FLV', '.mpg', '.avi')
        if os.path.exists(tip):
            if tip.endswith(exten):
                return True
        return False

    def open_file(self):
        ''' Open file with menu ... '''
        if self.dirpathmovies.get()=='':
            dirpath='.'
        else:
            dirpath = self.dirpathmovies.get()
        file = filedialog.askopenfile(initialdir=dirpath, title='select file', 
                                        filetypes={('flv','*.flv'), ('mp4','*.mp4'),
                                        ('avi','*.avi'), ('mpg','*.mpg')}, 
                                        defaultextension='*.mp4')
        print(file)
        if not file == None:
            if os.path.exists(file.name):
                self.video_source = file.name
                self.dirpathmovies.set(os.path.dirname(self.video_source))
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
        # print('>> scale onScale type val ->', type(val), val)
        if not self.vid:
            return
        try:
            # self.active_scale = True
            self.vid.seek(pts=float(val))
            # self.active_scale = False
        except Exception as e:
            print(e)
            # self.active_scale = False
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
        # put image play_b in btn_toogle_pause
        self.btn_toogle_pause['image'] = self.photos._play
        # load video stream
        self.vid = VideoStream(self.video_source)
        # set delay using
        self.delay = self.vid.f_rate
        # set scale value.
        self.var_t.set(0.1)
        # get and set duration video stream
        self.duracion = self.vid.duration
        # print time duration
        print('>> newplay: self.duracion ->', self.duracion)
        # set value maximun scale to
        self.scale.configure(to=self.duracion)
        # print configure values scale
        # print('>> self.scale.configure ->', self.scale)
        # ajuste valores de sonido al nivel seleccionado.
        self.vid.player.set_volume(float(self.soundvar.get()))
        # dimension vertical ventana.
        h = self.conten_controls.winfo_height()
        h_f = self.vid.h + h + 2
        w_f = self.vid.w + 2
        cad = f'{w_f}x{h_f}'
        self._width = w_f
        self._height = h_f
        self.master.geometry(cad)
        self.canvas.config(width=self.vid.w, height=self.vid.h)

    def snapshot(self):
        '''
        Get a frame from the video source
        '''
        # Get a frame from the video source
        #frame = self.vid.get_frame()[2]
        if not self.vid:
            return
        frame = self.imagen.copy()
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
        if self.dirImages is not None:
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
            pass
        else:
            self.val, self.pts, frame = self.vid.get_frame()

            if frame is not None and not self.active_scale:
                size = frame.get_size()
                arr = frame.to_memoryview()[0] # array image
                self.imagen = Image.frombytes("RGB", size, arr.memview)
                self.canvas.delete(tk.ALL) # borra todos los objetos con ese tags....
                self.imagen_copy = self.imagen.copy()
                w = self.canvas.winfo_width()
                h = self.canvas.winfo_height()
                marco = w, h  # marco de ventana
                self.imagen_copy = self.imagen.copy()
                self.imagen_copy = image_adjustment(self.imagen_copy, marco)
                self.photo = ImageTk.PhotoImage(self.imagen_copy)
                self.canvas.create_image(w/2, h/2, anchor='center', image = self.photo, tags='img')
                # print('>>> self.active_scale:', self.active_scale)
                # if not self.active_scale:
                self.var_t.set(self.pts)

        self.master.after(self.delay, self.update)


import sys

if __name__ == '__main__':
    # Create a window and pass it to the Application object
    source_v = None
    argv = list(reversed(sys.argv))
    print('init argument:', argv)
    while len(argv)>0:
        arg = argv.pop()
        if os.path.isfile(arg):
            ext = ('.mp4', '.MP4', '.flv', '.FLV', '.mpeg', '.MPEG', '.avi', '.AVI')
            # es un fichro.
            if arg.endswith(ext):
                # es un video
                source_v = arg
                print('argumentos:', source_v)
        
    root = tk.Tk()
    ScreenPlayer(root, title="Tkinter and ffpyplayer < Flash player >", video=source_v)
