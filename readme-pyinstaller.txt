# creamos el fichero spec para la compilacion como sigue: 
pyi-makespec --onefile --icon=./pirate-10.ico viewerplayer.py
# hacemos las modificaciones en el fichero viewerplayer y compilamos como sigue:
pyinstaller --onefile viewerplayer.spec
