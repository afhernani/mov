#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ffpyplayer.player import MediaPlayer
from PIL import Image
import time
import os

__version__ = '1.0'

class VideoStream:
    def __init__(self, video_source=0):
        ff_opts = {'paused' : True} # Audio options
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
                self.imagen, self.t = self.l_frame
                arr = self.imagen.to_memoryview()[0] # array image
                self.imagen = Image.frombytes("RGB", (self.w, self.h), arr.memview)
                # self.imagen.show()
                cond = False
        

    def get_frame(self):
        '''
        Return valores:
            val : 'eof' end sound
            t : time location.
            imagen : frame image
        Return (val, t, imagen)
        '''
        self.l_frame, self.val = self.player.get_frame()
        if self.val == 'eof':
            # condicion final fichero, salimos if and while
            self.player.toggle_pause() # ponemos en pause
            self.t = None
            self.imagen = None
            return self.val, self.t, self.imagen 
        elif self.l_frame is None:
            time.sleep(0.01)
            return self.val, self.t, None
        else:
            self.imagen, self.t = self.l_frame
            arr = self.imagen.to_memoryview()[0] # array image
            self.imagen = Image.frombytes("RGB", (self.w, self.h), arr.memview)
            # self.imagen.show()
            return self.val, self.t, self.imagen
        

    def toggle_pause(self):
        '''
            Function: toggle_pause
        '''
        try: # Stopping audio
            self.player.toggle_pause()
            # self.player = None
        except:
            pass
    
    def snapshot(self):
        '''
        Nothing for now
        '''
        pass

    # Release the video source when the object is destroyed
    def __del__(self):
        self.player.close_player()
        print('__del__')


if __name__ == '__main__':
    video = VideoStream('_Work/tem.mp4')
