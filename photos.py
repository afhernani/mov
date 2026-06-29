#!/usr/bin/env python3
import tkinter as tk
import os, sys
from PIL import Image, ImageTk, ImageDraw


__author__ = 'Hernani Aleman Ferraz'
__email__ = 'afhernani@gmail.com'
__apply__ = 'Flash - player'
__version__ = '1.3'


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def create_fallback_image(width=32, height=32, color='gray', text='?'):
    """
    Crea una imagen de color sólido con texto como fallback
    Args:
        width: Ancho de la imagen
        height: Alto de la imagen
        color: Color de fondo (nombre o hex)
        text: Texto a mostrar en el centro
    Returns:
        tk.PhotoImage: Imagen de fallback
    """
    # Crear imagen PIL
    img = Image.new('RGBA', (width, height), color)
    
    # Dibujar texto en el centro (opcional)
    if text:
        draw = ImageDraw.Draw(img)
        # Usar fuente por defecto
        try:
            # Intentar usar una fuente más grande
            from PIL import ImageFont
            font = ImageFont.load_default()
        except:
            font = None
        
        # Calcular posición del texto
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        draw.text((x, y), text, fill='white', font=font)
    
    # Convertir a PhotoImage de Tkinter
    return ImageTk.PhotoImage(img)

class Photos():
    """
    Gestor de imágenes de la aplicación con fallback automático
    """
    
    # Configuración de imágenes
    IMAGE_CONFIG = {
        '_apply': {'file': 'Images/apply_b.png', 'color': '#4CAF50', 'text': '✓'},
        '_play': {'file': 'Images/play_b.png', 'color': '#2196F3', 'text': '▶'},
        '_pause': {'file': 'Images/pause_b.png', 'color': '#FF9800', 'text': '⏸'},
        '_snapshot': {'file': 'Images/snapshot_b.png', 'color': '#9C27B0', 'text': '📷'},
        '_repeat': {'file': 'Images/repeat_b.png', 'color': '#00BCD4', 'text': '🔄'},
        '_open': {'file': 'Images/open_b.png', 'color': '#795548', 'text': '📂'},
        '_volume': {'file': 'Images/sound_b.png', 'color': '#607D8B', 'text': '🔊'},
    }
    
    def __init__(self, size=32):
        """
        Inicializa el gestor de imágenes
        Args:
            size: Tamaño estándar de los iconos (ancho y alto)
        """
        self.size = size
        self.failed_images = []  # Lista de imágenes que fallaron
        
        # Cargar cada imagen con fallback
        for attr_name, config in self.IMAGE_CONFIG.items():
            self._load_image(attr_name, config)
        
        # Cargar el logo (imagen grande, no icono)
        self._load_logo()
        
        # Reportar errores si los hubo
        if self.failed_images:
            print(f"⚠️  Advertencia: {len(self.failed_images)} imagen(es) no encontrada(s):")
            for img_name in self.failed_images:
                print(f"   - {img_name}")
    
    def _load_image(self, attr_name, config):
        """
        Carga una imagen o crea un fallback si falla
        Args:
            attr_name: Nombre del atributo (ej: '_play')
            config: Diccionario con configuración de la imagen
        """
        file_path = resource_path(config['file'])
        color = config.get('color', 'gray')
        text = config.get('text', '?')
        
        try:
            # Intentar cargar la imagen real
            if os.path.exists(file_path):
                img = tk.PhotoImage(file=file_path)
                setattr(self, attr_name, img)
            else:
                raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
                
        except Exception as e:
            # Si falla, crear fallback
            print(f"Error cargando {attr_name}: {e}")
            self.failed_images.append(config['file'])
            fallback = create_fallback_image(
                width=self.size,
                height=self.size,
                color=color,
                text=text
            )
            setattr(self, attr_name, fallback)
    
    def _load_logo(self):
        """
        Carga el logo de la aplicación con fallback
        """
        logo_path = resource_path('Images/flash.png')
        
        try:
            if os.path.exists(logo_path):
                self._logo = Image.open(logo_path)
            else:
                raise FileNotFoundError(f"Logo no encontrado: {logo_path}")
                
        except Exception as e:
            print(f"Error cargando logo: {e}")
            self.failed_images.append('Images/flash.png')
            # Crear logo fallback (imagen más grande)
            self._logo = Image.new('RGB', (200, 200), '#333333')
            draw = ImageDraw.Draw(self._logo)
            draw.text((50, 90), "FLASH", fill='white')
    
    def get_status(self):
        """
        Retorna el estado de carga de imágenes
        Returns:
            dict: Diccionario con estado de cada imagen
        """
        return {
            'total_images': len(self.IMAGE_CONFIG) + 1,  # +1 por el logo
            'failed_images': len(self.failed_images),
            'failed_list': self.failed_images.copy(),
            'all_loaded': len(self.failed_images) == 0
        }


if __name__ == '__main__':
    # Prueba del módulo
    root = tk.Tk()
    root.title("Test Photos Manager")
    
    # Crear instancia
    photos = Photos(size=48)
    
    # Mostrar estado
    status = photos.get_status()
    print(f"\nEstado de carga:")
    print(f"  Total imágenes: {status['total_images']}")
    print(f"  Fallidas: {status['failed_images']}")
    print(f"  Todas cargadas: {status['all_loaded']}")
    
    # Crear interfaz de prueba
    frame = tk.Frame(root)
    frame.pack(padx=20, pady=20)
    
    # Mostrar todos los iconos
    row = 0
    for attr_name in photos.IMAGE_CONFIG.keys():
        img = getattr(photos, attr_name)
        label = tk.Label(frame, image=img, text=attr_name, compound='top')
        label.grid(row=row, column=0, padx=10, pady=5)
        row += 1
    
    # Mostrar logo
    logo_tk = ImageTk.PhotoImage(photos._logo.resize((100, 100)))
    logo_label = tk.Label(frame, image=logo_tk, text="Logo", compound='top')
    logo_label.grid(row=row, column=0, padx=10, pady=20)
    
    root.mainloop()
