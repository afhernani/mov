#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ffpyplayer.player import MediaPlayer
from ffpyplayer import pic
from PIL import Image
import time
import os

__author__ = 'Hernani Aleman Ferraz'
__email__ = 'afhernani@gmail.com'
__version__ = '1.1'

class VideoStream:
    def __init__(self, video_source=0):
        ff_opts = {'paused' : True} # Audio options
        self.video_surce = video_source
        # variables size imagen
        self.original_size = None
        self.new_size = None
        # Open the video source
        self.player = MediaPlayer(video_source, ff_opts=ff_opts)
        # TODO: colocar pausa de tiempo para cargas mediaplayer y obtener los datos
        # conseguir el frame rate para la sincronizacion self.dalay
        while self.player.get_metadata()['src_vid_size'] == (0, 0):
            time.sleep(0.01)
        data  = self.player.get_metadata()
        print('data -->', data)
        self.f_rate = int(data['frame_rate'][0]/data['frame_rate'][1])
        print('delay -> ', self.f_rate)
        self.w, self.h = data['src_vid_size']
        print('WxH -> ', self.w, self.h)
        self.pts = self.player.get_pts() # Returns the elapsed play time. float
        print('pts ->', self.pts)
        self.duration = data['duration']
        print('duration', self.duration)
        self.pause = self.player.get_pause() # Returns whether the player is paused.
        print('pause ->', self.pause)
        self.volume = self.player.get_volume() # Returns the volume of the audio. loat: A value between 0.0 - 1.0
        print('volume ->', self.volume)
        self.player.toggle_pause() # Toggles -alterna- the player’s pause state
        # self.player.set_pause(False) # auses or un-pauses the file. state: bool
        cond = True
        while cond:
            self.l_frame, self.val = self.player.get_frame()
            if self.val == 'eof':
                print('can not open source: ', video_source)
                break
            elif self.l_frame is None:
                time.sleep(0.01)
            else:
                _imagen, self.pts = self.l_frame
                print('pts ->', self.pts)
                self.original_size = _imagen.get_size()
                arr = _imagen.to_memoryview()[0] # array image
                self.imagen = Image.frombytes("RGB", self.original_size, arr.memview)
                # self.imagen.show()
                cond = False

    def resize_imagen(self, img_rs, size=None):
        # si size no es none actualiza new_size
        if size:
            self.new_size = size
        # the same image
        if self.original_size == self.new_size:
            self.new_size = None # save operations
            return img_rs
        # if player not initializade return None imagen
        if not self.player:
            return None
        if img_rs is not None:
            try:
                size = img_rs.get_size()
                sws = None
                if self.new_size[0] > self.new_size[1]:
                    sws = pic.SWScale(size[0], size[1], img_rs.get_pixel_format(), ow=self.new_size[0])
                else:
                    sws = pic.SWScale(size[0], size[1], img_rs.get_pixel_format(), oh=self.new_size[1])
                img_res = sws.scale(img_rs)
                return img_res
            except Exception as ex:
                print('>>videostream: resize_imagen: ->', ex)
                img_rs = None
            return img_rs 

    def get_original_size(self):
        '''
        return (w, h) imagen
        or None is not stablished
        '''
        return self.original_size

    def set_new_size(self, size=None):
        '''
        set the new size imagen return
        size = (w, h)
        '''
        if size is not None:
            self.new_size = size


    def get_frame(self):
        '''
        Return valores:
            val : 'eof' or 'pause' 
            pts : time location aduio imagen.
            imagen : frame image
        Return (val, t, imagen)
        '''
        self.l_frame, self.val = self.player.get_frame()
        if self.val == 'eof':
            # condicion final fichero, salimos if and while
            # self.player.toggle_pause() # ponemos en pause
            return self.val, None, None 
        elif self.l_frame is None:
            time.sleep(0.01)
            return self.val, None, None
        else:
            _imagen, self.pts = self.l_frame
            if self.new_size is not None:
                _imagen = self.resize_imagen(_imagen)
            size = _imagen.get_size()
            arr = _imagen.to_memoryview()[0] # array image
            self.imagen = Image.frombytes("RGB", size, arr.memview)
            # print('>>> videostream::get_frame()::self.pts ->', self.pts)
            return self.val, self.pts, self.imagen
        

    def toggle_pause(self):
        '''
            Function: toggle_pause
        '''
        try: # Stopping audio
            self.player.toggle_pause()
            # self.player = None
        except:
            pass
    
    def seek(self, pts=None, relative=False, accurate=False):
        if not pts:
            return
        self.player.seek(pts, relative=False, accurate=False)

    def snapshot(self, road=None):
        '''
        get current frame
        '''
        img = self.l_frame[0]
        if img is not None:
            size = img.get_size()
            arr = img.to_memoryview()[0] # array image
            img = Image.frombytes("RGB", size, arr.memview)
            # vamos a guardar esto.
            time_str = time.strftime("%d-%m-%Y-%H-%M-%S")
            frame_name  = f"frame-{time_str}.jpg"
            if not road:
                ruta = os.path.dirname(self.video_surce)
                name_out = os.path.join(ruta, frame_name)
            else:
                name_out = os.path.join(road, frame_name)
            img.save(name_out)
        

    # Release the video source when the object is destroyed
    def __del__(self):
        self.player.close_player()
        print('__del__')


if __name__ == '__main__':
    video = VideoStream('_Work/tem.mp4')
