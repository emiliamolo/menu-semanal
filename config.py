import os

class Config:
    # Ruta base para persistencia (por defecto es la carpeta actual, 
    # pero en Render será algo como /var/lib/recipes o /data)
    DATA_PATH = os.environ.get('DATA_PATH', os.path.dirname(os.path.abspath(__file__)))
    
    # Aseguramos que el directorio exista
    DB_DIR = os.path.join(DATA_PATH, 'db')
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR, exist_ok=True)
        
    DB_PATH = os.path.join(DB_DIR, 'recetas.db')
    
    # Carpeta de imágenes en el volumen persistente
    UPLOAD_FOLDER = os.path.join(DATA_PATH, 'static', 'img', 'recetas')
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key')
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
