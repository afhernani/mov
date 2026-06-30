#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo centralizado de configuración y logging para Flash Player.
Compatible con desarrollo local y PyInstaller.

Uso:
    from config import AppConfig
    config = AppConfig()
    config.get('window', 'width')
    config.set('window', 'width', 800)
"""

import os
import sys
import configparser
import logging
from logging.handlers import RotatingFileHandler

__author__ = 'Hernani Aleman Ferraz'
__email__ = 'afhernani@gmail.com'
__apply__ = 'Flash - player'
__version__ = '1.3'


def get_app_dir():
    """
    Obtiene el directorio de la aplicación.
    - En desarrollo: el directorio del script.
    - En PyInstaller: el directorio donde está el ejecutable.
    
    Returns:
        str: Ruta absoluta al directorio de la aplicación.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller: el ejecutable está en sys.executable
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # Desarrollo: el script está en __file__
        return os.path.dirname(os.path.abspath(__file__))


def get_resource_path(relative_path):
    """
    Obtiene la ruta absoluta a un recurso (imágenes, etc.).
    Funciona tanto en desarrollo como en PyInstaller.
    
    Args:
        relative_path: Ruta relativa al recurso.
    Returns:
        str: Ruta absoluta al recurso.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller almacena los recursos en sys._MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class AppConfig:
    """
    Gestor centralizado de configuración y logging.
    
    Maneja:
    - Lectura/escritura de config.ini
    - Configuración de logging (consola + archivo)
    - Valores por defecto para todos los parámetros
    """
    
    # ──────────────────────────────────────────────
    # VALORES POR DEFECTO
    # ──────────────────────────────────────────────
    DEFAULTS = {
        'window': {
            'width': '400',
            'height': '400',
            'pos_x': '231',
            'pos_y': '231',
        },
        'paths': {
            'last_video_dir': '',
            'last_image_dir': '',
        },
        'player': {
            'volume': '0.9',
            'last_video': '',
        },
        'logging': {
            'level': 'INFO',
            'max_bytes': '1048576',    # 1 MB
            'backup_count': '3',
        },
    }
    
    _instance = None  # Para patrón Singleton
    
    def __new__(cls, *args, **kwargs):
        """Singleton: solo una instancia de AppConfig en toda la app."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_filename='config.ini', log_filename='app.log'):
        """
        Inicializa la configuración y el logging.
        
        Args:
            config_filename: Nombre del archivo de configuración.
            log_filename: Nombre del archivo de log.
        """
        if self._initialized:
            return
        
        self.app_dir = get_app_dir()
        self.config_path = os.path.join(self.app_dir, config_filename)
        self.log_path = os.path.join(self.app_dir, log_filename)
        
        # Inicializar configparser
        self._config = configparser.ConfigParser()
        self._load_defaults()
        self._load_config()
        
        # Inicializar logging
        self._setup_logging()
        
        self._initialized = True
        
        self.logger.info(f'AppConfig inicializado')
        self.logger.info(f'  App dir: {self.app_dir}')
        self.logger.info(f'  Config:  {self.config_path}')
        self.logger.info(f'  Log:     {self.log_path}')
    
    # ──────────────────────────────────────────────
    # CONFIGPARSER: Lectura / Escritura
    # ──────────────────────────────────────────────
    
    def _load_defaults(self):
        """Carga los valores por defecto en el configparser."""
        for section, values in self.DEFAULTS.items():
            if not self._config.has_section(section):
                self._config.add_section(section)
            for key, value in values.items():
                self._config.set(section, key, value)
    
    def _load_config(self):
        """Lee el archivo config.ini si existe, sobreescribiendo los defaults."""
        if os.path.exists(self.config_path):
            try:
                self._config.read(self.config_path, encoding='utf-8')
            except Exception as e:
                # Si el archivo está corrupto, usar defaults
                print(f'⚠️  Error leyendo config.ini: {e}')
                self._load_defaults()
    
    def save(self):
        """Guarda la configuración actual en config.ini."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self._config.write(f)
        except Exception as e:
            if hasattr(self, 'logger'):
                self.logger.error(f'Error guardando config.ini: {e}')
            else:
                print(f'❌ Error guardando config.ini: {e}')
    
    def get(self, section, key, fallback=None):
        """
        Obtiene un valor de configuración.
        
        Args:
            section: Sección del config (ej: 'window').
            key: Clave dentro de la sección (ej: 'width').
            fallback: Valor por defecto si no existe.
        Returns:
            str: El valor de configuración.
        """
        return self._config.get(section, key, fallback=fallback)
    
    def getint(self, section, key, fallback=0):
        """Obtiene un valor entero."""
        try:
            return self._config.getint(section, key, fallback=fallback)
        except (ValueError, TypeError):
            return fallback
    
    def getfloat(self, section, key, fallback=0.0):
        """Obtiene un valor flotante."""
        try:
            return self._config.getfloat(section, key, fallback=fallback)
        except (ValueError, TypeError):
            return fallback
    
    def getboolean(self, section, key, fallback=False):
        """Obtiene un valor booleano."""
        try:
            return self._config.getboolean(section, key, fallback=fallback)
        except (ValueError, TypeError):
            return fallback
    
    def set(self, section, key, value):
        """
        Establece un valor de configuración.
        
        Args:
            section: Sección del config.
            key: Clave.
            value: Valor (se convierte a string).
        """
        if not self._config.has_section(section):
            self._config.add_section(section)
        self._config.set(section, key, str(value))
    
    # ──────────────────────────────────────────────
    # LOGGING
    # ──────────────────────────────────────────────
    
    def _setup_logging(self):
        """Configura el sistema de logging (consola + archivo)."""
        log_level_str = self.get('logging', 'level', 'INFO')
        log_level = getattr(logging, log_level_str.upper(), logging.INFO)
        max_bytes = self.getint('logging', 'max_bytes', 1048576)
        backup_count = self.getint('logging', 'backup_count', 3)
        
        # Logger raíz de la aplicación
        self.logger = logging.getLogger('flashplayer')
        self.logger.setLevel(log_level)
        
        # Evitar duplicar handlers si se reinicializa
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Formato común
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler 1: Consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Handler 2: Archivo con rotación
        try:
            file_handler = RotatingFileHandler(
                self.log_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f'⚠️  No se pudo crear el archivo de log: {e}')
    
    # ──────────────────────────────────────────────
    # MÉTODOS DE CONVENIENCIA (atajos)
    # ──────────────────────────────────────────────
    
    def save_window_geometry(self, width, height, pos_x, pos_y):
        """Guarda la geometría de la ventana."""
        self.set('window', 'width', width)
        self.set('window', 'height', height)
        self.set('window', 'pos_x', pos_x)
        self.set('window', 'pos_y', pos_y)
        self.save()
        self.logger.debug(f'Geometría guardada: {width}x{height}+{pos_x}+{pos_y}')
    
    def get_window_geometry(self):
        """
        Obtiene la geometría de la ventana.
        
        Returns:
            str: String de geometría tipo '422x624+629+231'
        """
        w = self.getint('window', 'width', 422)
        h = self.getint('window', 'height', 624)
        x = self.getint('window', 'pos_x', 629)
        y = self.getint('window', 'pos_y', 231)
        return f'{w}x{h}+{x}+{y}'
    
    def save_last_video_dir(self, path):
        """Guarda el último directorio de videos."""
        if path:
            self.set('paths', 'last_video_dir', path)
            self.save()
    
    def get_last_video_dir(self):
        """Obtiene el último directorio de videos."""
        path = self.get('paths', 'last_video_dir', '')
        if path and os.path.exists(path):
            return path
        return os.path.expanduser('~')
    
    def save_last_image_dir(self, path):
        """Guarda el último directorio de imágenes."""
        if path:
            self.set('paths', 'last_image_dir', path)
            self.save()
    
    def get_last_image_dir(self):
        """Obtiene el último directorio de imágenes."""
        path = self.get('paths', 'last_image_dir', '')
        if path and os.path.exists(path):
            return path
        return os.path.expanduser('~')
    
    def save_volume(self, volume):
        """Guarda el volumen actual."""
        self.set('player', 'volume', round(float(volume), 2))
        self.save()
    
    def get_volume(self):
        """Obtiene el volumen guardado."""
        return self.getfloat('player', 'volume', 0.9)
    
    def save_last_video(self, path):
        """Guarda la ruta del último video reproducido."""
        if path:
            self.set('player', 'last_video', path)
            self.save()
    
    def get_last_video(self):
        """Obtiene la ruta del último video reproducido."""
        return self.get('player', 'last_video', '')


# ──────────────────────────────────────────────
# FUNCIÓN AUXILIAR GLOBAL PARA LOGGING
# ──────────────────────────────────────────────

def get_logger(name=None):
    """
    Obtiene un logger hijo del logger principal.
    
    Uso:
        logger = get_logger(__name__)
        logger.info('Mensaje informativo')
        logger.error('Error occurred')
    
    Args:
        name: Nombre del logger (usualmente __name__).
    Returns:
        logging.Logger
    """
    if name:
        return logging.getLogger(f'flashplayer.{name}')
    return logging.getLogger('flashplayer')