#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
import os
import sys
from PIL import Image, ImageTk, ImageDraw
from config import get_resource_path, get_logger

__author__ = 'Hernani Aleman Ferraz'
__email__ = 'afhernani@gmail.com'
__apply__ = 'Flash - player'
__version__ = '1.3'

logger = get_logger('photos')


def create_fallback_image(width=32, height=32, color='gray', text='?'):
    """Crea una imagen de color sólido con texto como fallback."""
    img = Image.new('RGBA', (width, height), color)
    if text:
        draw = ImageDraw.Draw(img)
        try:
            from PIL import ImageFont
            font = ImageFont.load_default()
        except Exception:
            font = None
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), text, fill='white', font=font)
    return ImageTk.PhotoImage(img)


class Photos:
    # ← CAMBIO: Images → Assets
    IMAGE_CONFIG = {
        '_apply':    {'file': 'Assets/apply_b.png',    'color': '#4CAF50', 'text': '⚡'},
        '_play':     {'file': 'Assets/play_b.png',     'color': '#2196F3', 'text': '▶'},
        '_pause':    {'file': 'Assets/pause_b.png',    'color': '#FF9800', 'text': '⏸'},
        '_snapshot': {'file': 'Assets/snapshot_b.png', 'color': '#9C27B0', 'text': '📷'},
        '_repeat':   {'file': 'Assets/repeat_b.png',   'color': '#00BCD4', 'text': '🔄'},
        '_open':     {'file': 'Assets/open_b.png',     'color': '#795548', 'text': '📂'},
        '_volume':   {'file': 'Assets/sound_b.png',    'color': '#607D8B', 'text': '🔊'},
    }
    
    # ← NUEVO: Configuración del icono de la aplicación
    APP_ICON_CONFIG = {
        'file': 'Assets/flash.png',  # ← El icono que vas a incluir
        'fallback_color': '#FF5722',
        'fallback_text': '⚡',
    }
    
    def __init__(self, size=32):
        self.size = size
        self.failed_images = []
        
        # Cargar iconos de botones
        for attr_name, cfg in self.IMAGE_CONFIG.items():
            self._load_image(attr_name, cfg)
        
        # ← NUEVO: Cargar icono de la aplicación
        self._load_app_icon()
        
        # Cargar logo
        self._load_logo()
        
        if self.failed_images:
            logger.warning(f'{len(self.failed_images)} imagen(es) no encontrada(s): '
                           f'{self.failed_images}')
        else:
            logger.info('Todas las imágenes cargadas correctamente')
    
    def _load_image(self, attr_name, cfg):
        """Carga una imagen o crea un fallback si falla."""
        file_path = get_resource_path(cfg['file'])
        color = cfg.get('color', 'gray')
        text = cfg.get('text', '?')
        
        try:
            if os.path.exists(file_path):
                img = tk.PhotoImage(file=file_path)
                setattr(self, attr_name, img)
            else:
                raise FileNotFoundError(f'No encontrado: {file_path}')
        except Exception as e:
            logger.error(f'Error cargando {attr_name}: {e}')
            self.failed_images.append(cfg['file'])
            fallback = create_fallback_image(self.size, self.size, color, text)
            setattr(self, attr_name, fallback)
    
    def _load_app_icon(self):
        """
        Carga el icono de la aplicación.
        Este icono se usará para:
        - Icono de la ventana (taskbar)
        - Icono en diálogos del sistema
        """
        icon_path = get_resource_path(self.APP_ICON_CONFIG['file'])
        
        try:
            if os.path.exists(icon_path):
                # Cargar como PhotoImage para Tkinter
                self._app_icon = tk.PhotoImage(file=icon_path)
                logger.info(f'Icono de aplicación cargado: {icon_path}')
            else:
                raise FileNotFoundError(f'Icono no encontrado: {icon_path}')
        except Exception as e:
            logger.error(f'Error cargando icono: {e}')
            self.failed_images.append(self.APP_ICON_CONFIG['file'])
            # Crear fallback
            fallback = create_fallback_image(
                64, 64,
                self.APP_ICON_CONFIG['fallback_color'],
                self.APP_ICON_CONFIG['fallback_text']
            )
            self._app_icon = fallback
    
    def _load_logo(self):
        """Carga el logo de la aplicación con fallback."""
        logo_path = get_resource_path('Assets/flash.png')  # ← CAMBIO: Images → Assets
        
        try:
            if os.path.exists(logo_path):
                self._logo = Image.open(logo_path)
            else:
                raise FileNotFoundError(f'Logo no encontrado: {logo_path}')
        except Exception as e:
            logger.error(f'Error cargando logo: {e}')
            self.failed_images.append('Assets/flash.png')
            self._logo = Image.new('RGB', (200, 200), '#333333')
            draw = ImageDraw.Draw(self._logo)
            draw.text((50, 90), "FLASH", fill='white')
    
    def get_app_icon(self):
        """
        Retorna el icono de la aplicación.
        
        Returns:
            tk.PhotoImage: Icono para usar en la ventana
        """
        return self._app_icon