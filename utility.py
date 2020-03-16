#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Hernani Aleman Ferraz'
__email__ = 'afhernani@gmail.com'
__apply__ = 'Flash - player'
__version__ = '1.2'

import sys
try:
    from PIL import Image
except ImportError:
    from pil import Image

def proportional_resizing(image, width=-1, height=-1):
    '''
    image to proportional resizing
    width, height.
    proportional w:-1, -1:h
    Return imagen in proportional resizing width, height
    '''
    # obtener datos.
    w_d = width # width_desired image
    h_d = height # height_desired image
    try:
        w_i, h_i = image.size
        if w_d != -1 and h_d !=-1:
            # 'proportional_resizing with w_o and h_o'
            pass
        elif w_d !=-1 and h_d == -1:
            # 'redimensionado proporcional en e w_o'
            p_w = float(w_d)/float(w_i)
            h_d = int(h_i * p_w)
        elif w_d == -1 and h_d != -1:
            # 'proportional resizing with h_o'
            p_h = float(h_d) / float(h_i)
            w_d = int( w_i * p_h)
        elif w_d ==-1 and h_d == -1:
            # 'the same image'
            return image
        image = image.resize((w_d, h_d), Image.ANTIALIAS)
        return image
    except IndexError as ider:
        print(ider)

def image_adjustment(imagen, size=None):
    '''
    size = (w, h)
    Image adjustment to a dimension frame width = w and height = h
    Return None or imagen adjustment.
    '''
    try:
        if size is not None:
            w, h = size
            if h <= 0:
                return None
        else:
            return None
        if imagen is not None:
            imagen_copy = imagen.copy()
        w_i, h_i = imagen.size
        r_sc = w/h
        r_im = w_i/h_i
        if r_im >=1:
            if r_sc >= r_im:
                imagen = proportional_resizing(imagen_copy, height=h)
            else:
                imagen = proportional_resizing(imagen_copy, width=w)
        elif r_im < 1:
            if r_sc < r_im:
                imagen = proportional_resizing(imagen_copy, width=w)
            else:
                imagen = proportional_resizing(imagen_copy, height=h)
        else:
            imagen = imagen_copy.resize((w, h), Image.ANTIALIAS)
    except IndexError as ider:
        print(ider)
        imagen = None
    return imagen

if __name__ == '__main__':
    image = Image.open('_Work/imagen/tumblr_oomj53OOUV1qkbpm3o1_1280.jpg')
    print('>> size original image:', image.size)
    image = proportional_resizing(image, width=400)
    print('>> size original to w=400, 400x400:', image.size)
    image.show()
    image = proportional_resizing(image, height=300)
    print('>> size original to h=300, 300x300:', image.size)
    image.show()
    image = proportional_resizing(image, height=150, width=200)
    print('>> size original 200x150:', image.size)
    image.show()
    
