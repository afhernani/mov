#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk, Image
import time
import os, signal, sys

from videostream import VideoStream
from photos import Photos
from utility import proportional_resizing
from utility import image_adjustment
from config import AppConfig, get_logger

__author__ = 'Hernani Aleman Ferraz'
__email__ = 'afhernani@gmail.com'
__apply__ = 'Flash - player'
__version__ = '1.3'

# ──────────────────────────────────────────────
# INSTANCIA GLOBAL DE CONFIGURACIÓN
# ──────────────────────────────────────────────
app_config = AppConfig()
logger = get_logger('viewerplayer')

# variable global para señal handler
app_instance = None

def signal_handler(signum, frame):
    """Maneja señales de terminación (Ctrl+C, kill, etc.)"""
    logger.warning(f'\n Señal de terminación recibida: {signum}')
    if app_instance and hasattr(app_instance, 'close'):
        app_instance.close()
    sys.exit(0)

# Registrar manejadores de señales
signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C
signal.signal(signal.SIGTERM, signal_handler)  # kill command


class ScreenPlayer(tk.Frame):
    
    def __init__(self, master=None, title=None, video=None):
        ''' Initialice window app '''
        super().__init__(master)        
        self.master = master
        # self.master.geometry('422x624+629+231') -> desarrollo ahead.
        self.pack(fill=tk.BOTH, expand=1)
        self.master.title(title)
        self.master['bg'] = 'Black'
        self.master.protocol('WM_DELETE_WINDOW', self.on_closing)
        self.master.protocol('WM_TAKE_FOCUS', self.confirmOpen)
        #self.master.protocol('WM_SAVE_YOURSELF', self.confirmSave)
        self.init = True
        self._closed = False # ← NUEVO: Flag para evitar doble cierre
        # self.setingfile = 'flash_seting.ini'
        # self.window.resizable(width=False, height=False)
        # Cargar configuración centralizada
        self.config = app_config
        self.logger = get_logger('ScreenPlayer')

        self.n_size = None
        self.photo = None
        self.photos = Photos()

        # self.master.call('wm', 'iconphoto', self.master, self.photos._apply)
        self.soundvar = tk.DoubleVar(value=0.9)
        self.master.wm_iconphoto(True, self.photos._apply)

        self.dirImages = None
        self.dirpathmovies = tk.StringVar(value=self.config.get_last_video_dir())  # directorio path video
        self.video_source = video
        # w = 350; h = 230; 
        self.duracion = 100.0
        self.active_scale = False
        self.vid = None
        self.val = 'paused'
        if self.video_source is not None:
            # open video source (by default this will try to open the computer webcam)
            try:
                self.dirpathmovies.set(os.path.dirname(self.video_source))
                self.config.save_last_video(self.video_source)
                self.vid = VideoStream(self.video_source)
                # w_f, h_f = self.vid.w, self.vid.h
                self.duracion = self.vid.duration
                self.soundvar.set(self.vid.player.get_volume())
                # Obtener primer frame
                frame = None
                while frame is None:
                    self.val, self.pts, frame = self.vid.get_frame()
                # Convertir usando el nuevo metodo
                self.imagen = self._convert_frame_to_pil(frame)

                #size = frame.get_size()
                #arr = frame.to_memoryview()[0] # array image
                #self.imagen = Image.frombytes("RGB", size, arr.memview)
                if self.imagen:
                    w_f, h_f = self.imagen.size
                    self.delay = self.vid.f_rate
                    self.vid.toggle_pause()
                    self._wxh = (w_f, (h_f + 40))
                    self._twh = (300, 300)
                else:
                    raise Exception("No se pudo cargar el primer frame")
                self.vid.toggle_pause()
            except Exception as e:
                self.logger.error(f"Error al cargar Video: {e}")
                self.video_source = None
                self.vid = None
        else:
            self.imagen = self.photos._logo
            w_f, h_f = self.imagen.size
            self.delay = 16
            self._wxh = (422, 624)
            self._twh = (629, 231)
        
        # ajuste ventana.
        # str_window = str(self._wxh[0])+ 'x'+str(self._wxh[1])+ '+' + str(self._twh[0])+ '+' + str(self._twh[1])
        # ← CAMBIAR: Usar geometría del config si no hay video
        if self.video_source is None:
            str_window = self.config.get_window_geometry()
        else:
            str_window = (f'{self._wxh[0]}x{self._wxh[1]}'
                          f'+{self._twh[0]}+{self._twh[1]}')
        
        self.master.geometry(str_window)
        self.logger.info(f'str ventana de inicio: {str_window}')
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
        
      
        #if self.video_source is None:
        #    self.get_init_status()
        self.update()
        self.master.mainloop()


    def confirmExit(self):
        if messagebox.askokcancel('Quit', 'Are you sure you want to exit?'):
            self.close()
            self.master.destroy()
        #self.set_init_status()
        #print('end process')

    def on_closing(self):
        """
        Manejador del evento de cierre de la ventana.
        Se ejecuta cuando el usuario hace clic en la X.
        """
        if messagebox.askokcancel('Salir', '¿Estás seguro de que quieres salir?'):
            self.close()
            self.master.destroy()

    def close(self):
        """
        Cierra la aplicación de forma segura, liberando todos los recursos.
        """
        if self._closed:
            return
        
        self.logger.info('Cerrando aplicación...')
        try:
            # 1. Guardar geometría de la ventana
            self._save_window_state()
            
            # 2. Guardar volumen
            self.config.save_volume(self.soundvar.get())
            
            # 3. Cerrar VideoStream
            if self.vid is not None:
                self.vid.close()
                self.vid = None
                self.logger.info('VideoStream cerrado')
            
            # 4. Limpiar imágenes
            self.imagen = None
            self.photo = None
            self.imagen_copy = None
            
            self.logger.info('Aplicación cerrada correctamente')
            
        except Exception as e:
            self.logger.error(f'Error crítico cerrando: {e}')
        finally:
            self._closed = True

    def _save_window_state(self):
        """Guarda el estado actual de la ventana en la configuración."""
        try:
            geo = self.master.geometry()
            # Parsear geometría: 'WIDTHxHEIGHT+X+Y'
            if '+' in geo:
                size_part, pos_part = geo.split('+', 1)
                w, h = size_part.split('x')
                x, y = pos_part.split('+')
                self.config.save_window_geometry(w, h, x, y)
            else:
                w, h = geo.split('x')
                self.config.save_window_geometry(w, h, 
                    self.master.winfo_x(), self.master.winfo_y())
        except Exception as e:
            self.logger.error(f'Error guardando geometría: {e}')

    def confirmOpen(self):
        '''here play the video if exist and window activate at init of app'''
        self.logger.info(f">> Confirm Open -- init:{self.init}")
        if self.init:
            if self.vid is not None:
                self.vid.toggle_pause()
                self.btn_toogle_pause['image'] = self.photos._play
            self.init=False


    def confirmSave(self):
        self.logger.info('>> push confirm Save.')

    def master_button_press(self, event):
        self.logger.info('>> master_button_press')

    def master_button_release(self, event):
        self.logger.info('>> master_button_release')

    def master_on_resize(self, event):
        _ventana = event.widget
        self.logger.info(f"[master_on_resize] {_ventana}")
        widget_size =(_ventana.winfo_width(), _ventana.winfo_height() )
        if str(_ventana) == '.!screenplayer.!canvas':
            self.logger.info('>> canvas:')
        m_wxh = (event.x, event.y)
        self.logger.info(f">> rezise:, {m_wxh}, {self._wxh}, widget_size:, {widget_size}")
        if self._wxh != m_wxh and str(_ventana) == '.!screenplayer.!canvas' and m_wxh == (0, 0):
            self.logger.info('>> on_resize_master ')
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
        self.logger.info('>> scale_button_press')
        self.active_scale = True
    
    def scale_button_release(self, event):
        self.logger.info('>> scale_button_release')
        self.active_scale = False
    
    def open_adjust_volumen(self):
        from overpanel import Over
        param = {'textvariable': self.soundvar}
        dialog = Over(master=self.master, cnf=param)
        dialog.mainloop()
    
    def soundvar_adjust(self, *args):
        """ Ajustar el volumen del video. """
        vol = self.soundvar.get()
        self.logger.debug(f'[sound adjust] -> {self.soundvar.get()}')
        if self.vid:
            self.vid.player.set_volume(vol)
            self.config.save_volume(vol)

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
        dirpath = self.config.get_last_video_dir()
        
        file = filedialog.askopenfile(initialdir=dirpath, 
                                        title='select file', 
                                        filetypes={('mp4','*.mp4'), ('flv','*.flv'), 
                                                   ('avi','*.avi'), ('mpg','*.mpg')}, 
                                        defaultextension='*.mp4')
        self.logger.info(f"fichero: {file}")
        if not file == None:
            if os.path.exists(file.name):
                self.video_source = file.name
                self.dirpathmovies.set(os.path.dirname(self.video_source))
                self.config.save_last_video_dir(self.dirpathmovies.get())
                self.config.save_last_video(str(file.name))
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
        self.logger.info(f'[onScale] type, val ->, {type(val)}, {val}')
        if not self.vid:
            return
        try:
            # self.active_scale = True
            self.vid.seek(pts=float(val))
            # self.active_scale = False
        except Exception as e:
            self.logger.error(f">> [onScale] exception: {e}")
            # self.active_scale = False
        # self.var_t.set(v)

    def replay(self):
        self.logger.info("[replay]")
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
        self.logger.info("[newplay]")
        # ← NUEVO: Cerrar el video anterior ANTES de cargar el nuevo
        if self.vid is not None:
            try:
                self.vid.close()
                self.vid = None
                self.logger.info('Video anterior cerrado antes de cargar nuevo')
            except Exception as e:
                self.logger.error(f'Error cerrando video anterior: {e}')
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
        self.logger.info(f'>> nuevo video: duracion = {self.duracion}')
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
            self.logger.warning('the video stream is closed')
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
        options['initialdir'] = self.config.get_last_image_dir()
               
        filesave = filedialog.asksaveasfilename(**options)
        
        if filesave:
            frame.save(filesave)
            self.config.save_last_image_dir(os.path.dirname(filesave))
            # actualiza directorio si este ha cambiado
            self.dirImages = os.path.dirname(filesave)
            self.logger.info(f"Snapshot guardado: {filesave}")
        
 
    def update(self):
        """
        Bucle principal de actualización del video
        Se ejecuta periódicamente usando root.after()
        """
        if not self.vid:
            # No hay video cargado, solo continuar el bucle
            self.master.after(self.delay, self.update)
            return
        
        # Obtener frame del video (sin time.sleep en el backend)
        val, pts, frame = self.vid.get_frame()
        
        # Procesar frame si está disponible y no estamos moviendo la barra
        if frame is not None and not self.active_scale:
            # Convertir frame a PIL Image
            self.imagen = self._convert_frame_to_pil(frame)
            
            if self.imagen:
                # Dibujar en canvas
                self._draw_canvas()
                
                # Actualizar tiempo actual
                if pts is not None:
                    self.var_t.set(pts)
        
        # Manejar fin de video
        elif val == 'eof':
            self.on_video_end()
            return  # Detener el bucle de actualización
        
        # Continuar el bucle de actualización
        self.master.after(self.delay, self.update)

        '''
        # Get a frame from the video source
        if self.vid and not self.active_scale:
            val, pts, frame = self.vid.get_frame()

            if frame is not None:
                # procesar y dibujar el frame
                self.imagen = self._convert_frame_to_pil(frame)
                self._draw_canvas()
                self.var_t.set(pts)
            elif val == 'eof':
                self.on_video_end()
                return # Detener el bucle
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
               
        # tkinter se encarga del timing. 
        # Si el video es 30fps, delay = 33ms.
        self.master.after(self.delay, self.update) '''

    def _convert_frame_to_pil(self, frame):
        """
        Convierte un frame de ffpyplayer a PIL Image
        Args:
            frame: Frame de ffpyplayer (objeto Image de ffpyplayer)
        Returns:
            PIL.Image.Image: Imagen en formato PIL
        """
        if frame is None:
            return None
        
        try:
            size = frame.get_size()
            arr = frame.to_memoryview()[0]  # array image
            imagen = Image.frombytes("RGB", size, arr.memview)
            return imagen
        except Exception as e:
            print(f"Error converting frame to PIL: {e}")
            return None

    def _draw_canvas(self):
        """
        Dibuja la imagen actual en el canvas, ajustándola al tamaño del canvas
        """
        if self.imagen is None:
            return
        
        try:
            # Obtener dimensiones del canvas
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            
            if w <= 0 or h <= 0:
                return
            
            # Limpiar canvas
            self.canvas.delete(tk.ALL)
            
            # Ajustar imagen al canvas manteniendo proporciones
            marco = (w, h)
            self.imagen_copy = self.imagen.copy()
            self.imagen_copy = image_adjustment(self.imagen_copy, marco)
            
            if self.imagen_copy is None:
                return
            
            # Convertir a PhotoImage y dibujar
            self.photo = ImageTk.PhotoImage(self.imagen_copy)
            self.canvas.create_image(w/2, h/2, anchor='center', image=self.photo, tags='img')
            
        except Exception as e:
            print(f"Error drawing canvas: {e}")

    def on_video_end(self):
        """
        Maneja el evento cuando el video termina de reproducirse
        """
        self.logger.info("Video ended")
        
        # Pausar el video
        if self.vid:
            self.vid.toggle_pause()
        
        # Cambiar botón a play
        self.btn_toogle_pause['image'] = self.photos._play
        self.val = 'paused'
        
        # Opcional: reiniciar al inicio
        # self.vid.seek(pts=0.0)
        # self.var_t.set(0.0)
        
        # Opcional: mostrar mensaje
        # messagebox.showinfo("Fin", "El video ha terminado")


import sys

if __name__ == '__main__':
    # Create a window and pass it to the Application object
    source_v = None
    argv = list(reversed(sys.argv))
    logger.info(f'init argument: {argv}')

    while len(argv)>0:
        arg = argv.pop()
        if os.path.isfile(arg):
            ext = ('.mp4', '.MP4', '.flv', '.FLV', '.mpeg', '.MPEG', '.avi', '.AVI')
            # es un fichro.
            if arg.endswith(ext):
                # es un video
                source_v = arg
                logger.info(f'argumentos: {source_v}')

    # ← NUEVO: Si no hay argumento, intentar cargar el último video
    if source_v is None:
        last_video = app_config.get_last_video()
        if last_video and os.path.exists(last_video):
            source_v = last_video
            logger.info(f'Cargando último video: {source_v}')

    root = tk.Tk()
    ScreenPlayer(root, title="Tkinter and ffpyplayer < Flash player >", video=source_v)
