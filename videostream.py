#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ffpyplayer.player import MediaPlayer
from ffpyplayer import pic
try:
    from PIL import Image
except ImportError:
    from pil import Image
import time
import os

__author__ = 'Hernani Aleman Ferraz'
__email__ = 'afhernani@gmail.com'
__apply__ = 'Flash - player'
__version__ = '1.2'

class VideoStream:
    def __init__(self, video_source=None):
        ff_opts = {'paused': True, 'autoexit': False}  # Audio options
        self.video_surce = video_source
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
                self._imagen, self.pts = self.l_frame
                print('pts ->', self.pts)
                # arr = self._imagen.to_memoryview()[0] # array image
                # self.imagen = Image.frombytes("RGB", self.original_size, arr.memview)
                # self.imagen.show()
                cond = False

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
            import math
            self._imagen, self.pts = self.l_frame
            return self.val, self.pts, self._imagen
            # w, h = self._imagen.get_size()
            # linesize = [int(math.ceil(w * 3 / 32.) * 32)]
            # self._imagen = pic.Image(plane_buffers=[bytes(b' ') * (h * linesize[0])],
            #             pix_fmt=self._imagen.get_pixel_format(), size=(w, h), linesize=linesize)
            # self._imagen.get_linesizes(keep_align=True)
            
            # if self.new_size is not None:
            #     sws = None
            #     n_w , n_h = self.new_size
            #     if n_w > n_h:
            #         sws = pic.SWScale(w, h, self._imagen.get_pixel_format(), oh=n_h)
            #     else:
            #         sws = pic.SWScale(w, h, self._imagen.get_pixel_format(), ow=n_w)
            #     self._imagen = sws.scale(self._imagen)

            # size = self._imagen.get_size()
            # arr = self._imagen.to_memoryview()[0] # array image
            # self.imagen = Image.frombytes("RGB", size, arr.memview)
            # print('>>> videostream::get_frame()::self.pts ->', self.pts)

        

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
